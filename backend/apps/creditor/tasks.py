import json
import logging

from apps.voxum_base.tasks import AbstractTask
from apps.voxum_base.utils import count_group_connections
from apps.creditor.models import Creditor
from apps.creditor.schemas import CreditorDetailSchema
from apps.meetings.models import RepresentativeMeeting
from apps.web_sockets.signals import update_creditor_detail, update_representative_meeting_detail
from apps.web_sockets.tasks import SendJsonMessageTask
from config.celery import app as celery_app, REDIS_CONN


class SendCreditorUserGuestDetail(AbstractTask):
    redis_conn = REDIS_CONN
    type = 'object'
    max_retries = 3

    def run(self, user_id, meeting_id):
        creditor = Creditor.objects.filter(meeting_id=meeting_id, guest__user_id=user_id).first()
        room = f'{meeting_id}__{user_id}'
        group_info = count_group_connections(room)

        if creditor:
            creditor_data = CreditorDetailSchema(creditor).data
            user_id = creditor.guest.user.id

            if group_info == 0:
                logging.debug(f'user {user_id} has no connected to meeting {meeting_id}')
            else:
                SendJsonMessageTask.delay('creditor_detail_guest', room,
                                          json.dumps(creditor_data, default=str), self.type)

            representatives_meeting = creditor.get_representatives_meeting()

            for representative_meeting in representatives_meeting:
                representative_user_id = representative_meeting.guest.user.id
                room_representative_meeting = f'{meeting_id}__{representative_user_id}'

                group_info = count_group_connections(room_representative_meeting)

                if group_info == 0:
                    logging.debug(f'user {representative_user_id} has no connected to meeting {meeting_id}')
                else:
                    self.send_representative_detail_guest(representative_meeting, room_representative_meeting, meeting_id)

        representative_meeting = RepresentativeMeeting.objects.filter(meeting_id=meeting_id,
                                                                      guest__user_id=user_id).first()
        if representative_meeting:
            self.send_representative_detail_guest(representative_meeting, room, meeting_id)

    def send_representative_detail_guest(self, representative_meeting, room, meeting_id):
        creditors = representative_meeting.get_creditors_by_meeting_id(meeting_id)
        representative_meeting_data = CreditorDetailSchema(creditors, many=True).data

        representative_meeting_detail_guest = {
            'creditors': representative_meeting_data,
            'has_presence': representative_meeting.has_presence,
            'all_creditors_accredited': representative_meeting.all_creditors_accredited,
        }
        SendJsonMessageTask.delay('representative_detail_guest', room,
                                  json.dumps(representative_meeting_detail_guest, default=str), self.type)


class GuestUpdateCreditorRepresentativesDetail(AbstractTask):
    max_retries = 3

    def run(self, msal_id):
        creditors = Creditor.objects.filter(guest__msaluserguest__id=msal_id)

        for creditor in creditors:
            update_creditor_detail.send(instance=creditor, sender=Creditor)

        representatives = RepresentativeMeeting.objects.filter(guest__msaluserguest__id=msal_id)

        for representative in representatives:
            update_representative_meeting_detail.send(instance=representative, sender=RepresentativeMeeting)


SendCreditorUserGuestDetailTask = celery_app.register_task(SendCreditorUserGuestDetail())
GuestUpdateCreditorRepresentativesDetailTask = celery_app.register_task(GuestUpdateCreditorRepresentativesDetail())