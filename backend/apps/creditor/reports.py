import logging

from apps.voxum_base.tasks import AbstractTask
from apps.meetings.report import MeetingReport
from apps.voting.report import VotingReport
from config.celery import app
from config.settings import DEFAULT_QUEUE_EXCEL


class RepresentativeReport(AbstractTask):
    default_retry_delay = 30
    queue = DEFAULT_QUEUE_EXCEL

    def run(self, meeting_id, report_id):
        meeting = MeetingReport(meeting_id, report_id, self.request.id)

        try:
            meeting.export()
            return {'success': True}
        except Exception as e:
            logging.critical(e, exc_info=True)
            try:
                self.retry()
            except self.MaxRetriesExceededError:
                meeting.meeting_report.save()
                raise e


class TaskVotingReport(AbstractTask):
    default_retry_delay = 30
    queue = DEFAULT_QUEUE_EXCEL

    def run(self, report_id):
        voting = VotingReport(report_id)

        try:
            voting.export()
            return {'success': True}
        except Exception as e:
            logging.critical(e, exc_info=True)
            try:
                self.retry()
            except self.MaxRetriesExceededError:
                voting.voting_report.save()
                raise e


RepresentativeReportTask = app.register_task(RepresentativeReport())
VotingReportTask = app.register_task(TaskVotingReport())