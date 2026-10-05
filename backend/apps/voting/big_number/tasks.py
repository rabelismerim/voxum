"""
Celery tasks for processing voting results and related operations.

These tasks utilize Celery for asynchronous processing and leverage
lock management to ensure task execution integrity.

Classes:
- ProcessVotingSetResult: Task for processing voting results by voting ID.
- ProcessVotingResult: Task for processing voting results by creditor ID.
- ProcessVotingResultByIds: Task for processing voting results by a list of voting IDs.

Usage:
1. Define tasks such as ProcessVotingSetResult, ProcessVotingResult, and ProcessVotingResultByIds.
2. Register tasks with Celery using celery_app.register_task.
3. Use .delay method to enqueue tasks asynchronously.

Example:
```python
from config.celery import app as celery_app

# Register tasks
ProcessVotingSetResultTask = celery_app.register_task(ProcessVotingSetResult())
ProcessVotingResultTask = celery_app.register_task(ProcessVotingResult())
ProcessVotingResultByIdsTask = celery_app.register_task(ProcessVotingResultByIds())

# Queue tasks asynchronously
ProcessVotingSetResultTask.delay(voting_id=123)
ProcessVotingResultTask.delay(creditor_id=456)
ProcessVotingResultByIdsTask.delay(voting_ids=[789, 890])
"""

from celery import Task

from apps.voxum_base.tasks import AbstractTask
from apps.creditor.models import Creditor
from apps.voting.models import Voting
from apps.web_sockets.signals import update_voting_progress_detail
from config.celery import app as celery_app


class ProcessVotingSetResult(AbstractTask):
    """
    Task for processing voting results by voting ID.

    Attributes:
    - max_retries (int): Maximum number of retries for task execution.
    - identifier (str): Identifier used for locking tasks.

    Methods:
    - run(voting_id): Executes the task logic for processing voting results.
    """
    max_retries = 3
    identifier = 'voting_id'

    def run(self, voting_id):
        """
        Executes the task logic for processing voting results.

        Args:
        - voting_id (int): ID of the voting to process.

        Returns:
        - str: Confirmation message after processing the voting.
        """
        voting = Voting.objects.filter(id=voting_id).first()

        results = voting.set_results()
        if voting.in_progress:
            update_voting_progress_detail.send(instance=voting, sender=Voting)

        return results


from apps.voxum_base.tasks import AbstractTask


class ProcessVotingResult(AbstractTask):
    """
    Task for processing voting results by creditor ID.

    Attributes:
    - max_retries (int): Maximum number of retries for task execution.

    Methods:
    - run(creditor_id): Executes the task logic for processing creditor's voting results.
    """

    max_retries = 3

    def run(self, creditor_id):
        """
        Executes the task logic for processing creditor's voting results.

        Args:
        - creditor_id (uuid): ID of the creditor whose votings to process.

        Returns:
        - str: Confirmation message after processing the creditor's votings.
        """

        creditor = Creditor.objects.filter(id=creditor_id).first()

        for voting in creditor.get_votings().values_list('id', flat=True):
            ProcessVotingSetResultTask.delay(voting)

        return f'creditor_id: {creditor_id}'


from apps.voxum_base.tasks import AbstractTask


class ProcessVotingResultByIds(AbstractTask):
    """
    Task for processing voting results by a list of voting IDs.

    Attributes:
    - max_retries (int): Maximum number of retries for task execution.

    Methods:
    - run(voting_ids): Executes the task logic for processing votings by IDs.
    """

    max_retries = 3

    def run(self, voting_ids):
        """
        Executes the task logic for processing votings by IDs.

        Args:
        - voting_ids (list): List of voting IDs to process.

        Returns:
        - str: Confirmation message after processing the votings.
        """

        votings = Voting.objects.filter(id__in=voting_ids).values_list('id', flat=True)

        for voting in votings:
            ProcessVotingSetResultTask.delay(voting)

        return f'votings: {votings}'


ProcessVotingResultTask = celery_app.register_task(ProcessVotingResult())
ProcessVotingResultByIdsTask = celery_app.register_task(ProcessVotingResultByIds())
ProcessVotingSetResultTask = celery_app.register_task(ProcessVotingSetResult())
