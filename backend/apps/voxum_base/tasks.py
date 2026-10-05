"""
Module: tasks

This module defines tasks and utilities for managing task execution and locking mechanisms using Celery and Redis.

Classes:
- LockManager: Manages locking using Redis for task synchronization.
- AbstractTask: Base class for defining Celery tasks with locking and identifier handling.

Utilities:
- REDIS_CONN: Redis connection used by the LockManager and AbstractTask for Redis operations.
"""

import inspect
import json
import logging
import threading

from celery import Task
from config.celery import app as celery_app

from config.celery import REDIS_CONN

redis_client = REDIS_CONN


class LockManager:
    """
    Utility class for managing locks using Redis.

    Attributes:
    - timeout (int): Timeout value in seconds for lock expiration.

    Methods:
    - acquire_lock(identifier): Attempts to acquire a lock for the given identifier.
    - release_lock(identifier): Releases the lock for the given identifier.
    """

    def __init__(self, timeout=60):
        self.timeout = timeout

    def acquire_lock(self, identifier):
        """
        Attempts to acquire a lock for the given identifier.

        Args:
        - identifier (str): Unique identifier for the lock.

        Returns:
        - bool: True if lock was acquired successfully, False if the lock already exists.
        """
        lock_key = f'{identifier}:lock'
        if celery_app.conf.task_always_eager:
            with self._local_locks_guard:
                if lock_key in self._local_locks:
                    logging.debug(f'Lock already acquired. Using key {lock_key}')
                    return False
                self._local_locks.add(lock_key)
                logging.debug(f'Lock acquired. Using key {lock_key}')
                return True

        if not redis_client.set(lock_key, 'true', ex=self.timeout, nx=True):
            logging.debug(f'Lock already acquired. Using key {lock_key}')
            return False
        logging.debug(f'Lock acquired. Using key {lock_key}')
        return True

    def release_lock(self, identifier):
        """
        Releases the lock for the given identifier.

        Args:
        - identifier (str): Unique identifier for the lock.
        """
        lock_key = f'{identifier}:lock'
        if celery_app.conf.task_always_eager:
            with self._local_locks_guard:
                self._local_locks.discard(lock_key)
        else:
            redis_client.delete(lock_key)
        logging.debug(f'Lock removed. Using key {lock_key}')

    _local_locks = set()
    _local_locks_guard = threading.Lock()


class SemaphoreManager:
    def __init__(self):
        self.semaphores = {}

    def get_semaphore(self, queue_name, max_semaphores=None):
        # Se max_semaphores for None, significa que não deve ser usado semáforo
        if max_semaphores is None or queue_name is None:
            return None

        if queue_name not in self.semaphores:
            self.semaphores[queue_name] = threading.Semaphore(max_semaphores)

        return self.semaphores[queue_name]


semaphore_manager = SemaphoreManager()


class AbstractTask(Task):
    redis_conn = REDIS_CONN

    max_retries = 3
    max_semaphores = None

    identifier = None
    identifier_key = None
    lock = LockManager()

    def __init__(self):
        self.max_semaphores = self.get_queue_concurrency()

    def get_queue_concurrency(self):
        task_queues = celery_app.conf.task_queues
        for queue in task_queues:
            if queue.name == self.get_queue_name():
                return getattr(queue, 'concurrency', None)
        return

    def get_identifier_prefix(self):
        """
        Returns the prefix to use for constructing the lock identifier.

        Returns:
        - str: Prefix string based on the class name.
        """
        return self.__class__.__name__

    def get_identifier(self, *args, **kwargs):
        """
        Constructs the full identifier key for locking based on task arguments.

        Args:
        - *args: Positional arguments passed to the task.
        - **kwargs: Keyword arguments passed to the task.

        Returns:
        - str: Full identifier key for locking based on task arguments.
        """

        identifier_key = kwargs.get('identifier_key', None)

        if identifier_key:
            return identifier_key

        if self.identifier:
            arg_names = inspect.getfullargspec(self.run).args

            identifier_value = kwargs.get(self.identifier)

            if identifier_value is None:

                if self.identifier in arg_names:
                    identifier_value = args[arg_names.index(self.identifier) - 1]
                else:
                    identifier_value = self.identifier

            identifier_key = f'{self.get_identifier_prefix()}:{identifier_value}'

            return identifier_key

    def delay(self, *args, **kwargs):
        """
        Queues the task with automatic locking based on the identifier.

        Args:
        - *args: Positional arguments passed to the task.
        - **kwargs: Keyword arguments passed to the task.

        Returns:
        - AsyncResult: Result object representing the queued task.
        """

        identifier_key = self.get_identifier(*args, **kwargs)
        logging.debug(f'Executing task in delay{identifier_key}')
        if identifier_key:
            acquire_lock = self.lock.acquire_lock(identifier_key)

            if not acquire_lock:
                return

        return super().delay(*args, **kwargs)

    def get_queue_name(self):
        return getattr(self, 'queue', None)

    def __call__(self, *args, **kwargs):
        """
        Executes the task and releases the lock after execution.

        Args:
        - *args: Positional arguments passed to the task.
        - **kwargs: Keyword arguments passed to the task.
        """

        identifier_key = self.get_identifier(*args, **kwargs)
        kwargs.pop('identifier_key', None)  # Remove identifier_key to prevent error identifier_key arguments in run
        semaphore = semaphore_manager.get_semaphore(self.get_queue_name(), self.max_semaphores)

        if semaphore:
            with semaphore:
                call = super().__call__(*args, **kwargs)
        else:
            call = super().__call__(*args, **kwargs)

        if identifier_key:
            self.lock.release_lock(identifier_key)
        return call

    def json_response(self, data):
        """
        Converts data to JSON format with proper handling of non-serializable types.

        Args:
        - data: Data to be converted to JSON.

        Returns:
        - dict: JSON representation of the data.
        """
        try:
            return json.loads(json.dumps(data, default=str))
        except TypeError:
            return data