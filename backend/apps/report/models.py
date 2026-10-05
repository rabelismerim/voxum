import logging
import os
import textwrap

from celery.result import AsyncResult
from django.core.files import File
from django.db import models
from django.db.models import TextChoices
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_celery_results.models import TaskResult

from apps.creditor.reports import RepresentativeReportTask, VotingReportTask
from apps.meetings.models import Meeting
from apps.report.conversor import ExcelWriter
from apps.voting.models import Voting
from config.celery import app as celery_app
from config.settings import MEDIA_ROOT
from core.abstract.models import AbstractModel


class ReportMeetingChoices(TextChoices):
    LIST_REPRESENTATIVE = 'R', 'Lista de Representantes'
    LIST_REPRESENTATIVE_PRESENT = 'P', 'Lista de Representantes Presentes'
    LIST_CREDITORS = 'C', 'Lista de Credores'
    LIST_CREDITORS_PRESENT = 'E', 'Lista de Credores Presentes'


class ReportVotingChoices(TextChoices):
    VOTING_DETAIL = 'R', 'Relatório de Votação Detalhado'
    VOTING_PRESENT_DETAIL = 'V', 'Votantes Presentes'
    VOTING_RESERVATION_DETAIL = 'D', 'Relatório de Votação Detalhado com ressalvas'
    VOTING_RESERVATION_PRESENT_DETAIL = 'P', 'Votantes Presentes com ressalvas'


class AbstractReport(AbstractModel):
    """
    Classe que representa um arquivo de relatório base.
    """
    file = models.FileField(upload_to='converter/pdf/%Y/%m/%d/', null=True, blank=True)
    task_result = models.ForeignKey(TaskResult, on_delete=models.SET_NULL, null=True, blank=True)
    task_id = models.UUIDField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.file.name or str(self.task_id) or str(self.id)

    def get_status_pending_task(self):
        """Obtém o status de uma tarefa de processamento pendente."""
        if not self.task_id:
            return {
                "task_id": self.task_id,
                "status": 'FAILURE',
                "get_status_display": 'FAILURE',
            }
        state = AsyncResult(id=str(self.task_id)).state
        return {
            "task_id": self.task_id,
            "status": state,
            "get_status_display": state,
        }

    @property
    def task(self):
        """Obtém os detalhes da tarefa de processamento associada."""
        return self.task_result or self.get_status_pending_task()


class ReportMeeting(AbstractReport):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=1, choices=ReportMeetingChoices.choices)

    @property
    def type_display(self):
        return self.get_report_type_display()

    @property
    def type(self):
        return self.report_type

    def save(self, *args, **kwargs):
        created_at = self.created_at
        save = super().save(*args, **kwargs)
        if not created_at:
            task = RepresentativeReportTask.delay(self.meeting.id, self.id)
            self.task_id = task.id
            save = super().save(*args, **kwargs)
        return save

    def run_task(self):
        if self.task_id:
            task_result = AsyncResult(self.task_id)
            if task_result.state in ['PENDING', 'STARTED', 'RETRY']:
                celery_app.backend.store_result(self.task_id,
                                                {'state': 'FAILURE', 'exc_message': 'Nova tarefa solicitada',
                                                 'exc_type': 'ValueError'}, state='FAILURE')

                task_result.revoke(terminate=True)

        task = RepresentativeReportTask.delay(self.meeting.id, self.id)
        self.task_id = task.id
        self.save()


class ReportVoting(AbstractReport):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=1, choices=ReportVotingChoices.choices)

    @property
    def type_display(self):
        return self.get_report_type_display()

    @property
    def type(self):
        return self.report_type

    def save(self, *args, **kwargs):
        created_at = self.created_at
        save = super().save(*args, **kwargs)
        if not created_at:
            task = VotingReportTask.delay(self.id)
            self.task_id = task.id
            save = super().save(*args, **kwargs)
        return save

    def run_task(self):
        if self.task_id:
            task_result = AsyncResult(self.task_id)
            if task_result.state in ['PENDING', 'STARTED', 'RETRY']:
                task_result.revoke(terminate=True)

        task = VotingReportTask.delay(self.id)
        self.task_id = task.id
        self.save()


class AbstractReportToPDF:
    meeting = None
    report = None
    columns_title = ['A', 'D']
    columns_date = ['G', 'J']
    title_fill_width = 45

    def __init__(self, report_id, name):
        self.report_id = report_id
        self.name = name
        self.report, meeting_id = self.get_meeting_report()
        task_id = self.report.task_id
        self.task_id = task_id
        self.meeting_id = meeting_id
        self.meeting = Meeting.objects.get(id=meeting_id)

        self.writer = ExcelWriter(folder=MEDIA_ROOT)

        self.set_right_headers()
        self.set_center_headers()
        self.set_meeting()
        self.set_start_data()
        self.set_location()
        self.set_observation()

    def get_meeting_report(self) -> tuple:
        pass

    def export(self):
        pdf_path = self.writer.save_as_pdf()
        logging.debug(f'pdf_path: {pdf_path}\n')
        with open(pdf_path, 'rb') as arquivo:
            filename = pdf_path.split('\\')[-1]
            self.report.file.save(filename, File(arquivo))

    def set_value(self, row, col, value, font=None, fill=None):
        self.writer.set_value(row, col, value, font=font, fill=fill)

    def set_center_headers(self):
        headers = f'&B{self.name}&B'.upper()
        self.writer.set_center_headers(headers)

    def set_meeting(self):
        meeting_name = f'{self.meeting.name}'.upper()
        text = f"Nome da Assembleia: {meeting_name}"
        text = self.wrap_title(text)
        fonte = self.writer.STILE.bold_black_font
        self.writer.set_value(1, self.columns_title, text, font=fonte, wrap_text=True, fill_width=self.title_fill_width)

    def set_start_data(self):
        text = f'Data Início: {self.meeting.start_date.strftime("%d/%m/%Y %H:%M:%S")}'
        text = self.wrap_title(text)
        fonte = self.writer.STILE.bold_black_font
        self.writer.set_value(1, self.columns_date, text, font=fonte, wrap_text=True, fill_width=self.title_fill_width)
        self.writer.set_repeat_title(1, 1)

    def set_location(self):
        location = f'{self.meeting.location.description}'.title()
        text = f"Local: {location}"
        text = self.wrap_title(text)
        fonte = self.writer.STILE.bold_black_font
        self.writer.set_value(3, self.columns_title, text, font=fonte, wrap_text=True, fill_width=self.title_fill_width)
        self.writer.set_repeat_title(3, 3)

    def set_observation(self):
        text = f"Observação: {self.meeting.description}"
        fonte = self.writer.STILE.bold_black_font
        text = self.wrap_title(text)
        self.writer.set_value(3, self.columns_date, text, font=fonte, wrap_text=True, fill_width=self.title_fill_width)

    def wrap_title(self, text):
        return '\n'.join(textwrap.wrap(text, self.title_fill_width))

    def set_right_headers(self):
        image = os.path.join(os.getcwd(), 'logo-1080.png')
        self.writer.set_img_right_headers(image)


class ReportMeetingToPDF(AbstractReportToPDF):
    report_id = None

    def get_meeting_report(self):
        report = ReportMeeting.objects.filter(id=self.report_id).first()
        meeting_id = report.meeting.id
        return report, meeting_id


class ReportVotingToPDF(AbstractReportToPDF):

    def get_meeting_report(self):
        report = ReportVoting.objects.filter(id=self.report_id).first()
        meeting_id = report.voting.meeting.id
        return report, meeting_id


@receiver(pre_delete, sender=TaskResult)
def remove_task_id(sender, **kwargs):
    instance = kwargs.get('instance')
    task_id = instance.task_id
    report = ReportMeeting.objects.filter(task_id=task_id).first()
    if report:
        report.task_id = None
        report.save()
        return

    report = ReportVoting.objects.filter(task_id=task_id).first()
    if report:
        report.task_id = None
        report.save()