import logging
import os

django_module = os.environ.get('DJANGO_SETTINGS_MODULE')

if not django_module:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()

from celery.signals import worker_ready

from celery import shared_task

from config.celery import app as celery_app
from config.settings import QUEUE_CELERY_VOXUM

__all__ = ("celery_app",)


@shared_task(queue=QUEUE_CELERY_VOXUM)
def start_celery():
    logging.info('||Started Voxum||\n\n')
    return True


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Start receiver voting listener"""
    start_celery.delay()
