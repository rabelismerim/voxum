from django.db.models.signals import post_save, post_delete

from apps.voxum_base.views_sockets import Schema
from apps.creditor.schemas import CreditorSchema
from apps.web_sockets.signals import update_creditor_detail, update_creditor_list


class CreditorDetail(Schema):
    serializer = CreditorSchema
    channel = 'creditor_list'
    filter_key = 'meeting_id'
    send_initial = False
    signals = [post_save, update_creditor_detail]
    type = 'array_update'

    def get_room(self):
        return self.instance.meeting.id

    def filter(self):
        return {self.filter_key: self.instance.meeting.id}


class CreditorListDetail(Schema):
    serializer = CreditorSchema
    channel = 'creditor_list'
    filter_key = 'meeting_id'
    send_initial = False
    signals = [update_creditor_list]
    type = 'array_create'
    many = True

    def get_room(self):
        return self.instance.meeting.id

    def filter(self):
        return {self.filter_key: self.instance.meeting.id}


class CreditorDeleteDetail(Schema):
    serializer = CreditorSchema
    channel = 'creditor_list'
    filter_key = 'meeting_id'
    send_initial = False
    signals = [post_delete]
    type = 'array_delete'

    def get_room(self):
        return self.instance.meeting.id

    def filter(self):
        return {self.filter_key: self.instance.meeting.id}