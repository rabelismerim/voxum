"""
Módulo de tarefas assíncronas para operações relacionadas a Assembleias.
"""
import json
import logging

from django.db.models import Q

from apps.voxum_base.tasks import AbstractTask
from apps.creditor.models import Representative, Creditor
from apps.meetings.models import Meeting
from apps.meetings.schemas import MeetingToGuestSchema
from apps.web_sockets.tasks import SendJsonMessageTask
from config.celery import app as celery_app, REDIS_CONN


class SendMeetingToAllUserGuest(AbstractTask):
    redis_conn = REDIS_CONN
    type = 'object'
    max_retries = 3
    identifier = 'meeting_id'

    def run(self, meeting_id):
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if not meeting:
            return

        meeting_data = MeetingToGuestSchema(meeting).data

        for creditor in meeting.creditor_set.filter(online=True):
            user_id = creditor.guest.user.id
            SendJsonMessageTask.delay('meeting_detail_guest', f'{meeting_id}__{user_id}',
                                      json.dumps(meeting_data, default=str), self.type)

        representative_user_ids = Representative.objects.filter(
            representative__meeting_id=meeting.id, online=True
        ).values_list('representative__guest__user_id', flat=True)

        for user_id in list(set(representative_user_ids)):
            SendJsonMessageTask.delay('meeting_detail_guest', f'{meeting_id}__{user_id}',
                                      json.dumps(meeting_data, default=str), self.type)


class SendMeetingUserGuestDetail(AbstractTask):
    redis_conn = REDIS_CONN
    type = 'object'
    max_retries = 3

    def run(self, meeting_id, user_id):
        meeting = Meeting.objects.filter(
            Q(creditor__guest__user__id=user_id, creditor__online=True) |
            Q(representativemeeting__guest__user__id=user_id, representativemeeting__representative__online=True),
            id=meeting_id
        ).first()

        if not meeting:
            logging.debug(f'user: {user_id} not connected to meeting: {meeting_id}')
            return

        meeting_data = MeetingToGuestSchema(meeting).data
        SendJsonMessageTask.delay('meeting_detail_guest', f'{meeting_id}__{user_id}',
                                  json.dumps(meeting_data, default=str), self.type)


class SetUsersOffline(AbstractTask):
    identifier = 'set_users_offline'
    priority = 1
    queue = 'default'

    def run(self):
        Creditor.objects.filter(online=True).update(online=False)
        Representative.objects.filter(online=True).update(online=False)


SendMeetingToAllUserGuestTask = celery_app.register_task(SendMeetingToAllUserGuest())
SendMeetingUserGuestDetailTask = celery_app.register_task(SendMeetingUserGuestDetail())
SetUsersOfflineTask = celery_app.register_task(SetUsersOffline())