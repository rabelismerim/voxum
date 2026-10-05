import logging
import time

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from support.schedule.models import SCHEDULER
        SCHEDULER.scheduler
        logging.critical('Started command handler')

        while True:
            time.sleep(1)