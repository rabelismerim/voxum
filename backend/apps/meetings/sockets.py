"""
Módulo de Sockets para manipulação de schemas de Assembleias e Representantes.
"""
from django.db.models.signals import post_save

from apps.voxum_base.views_sockets import Schema
from apps.meetings.schemas import MeetingSchema, ClasseSchema, RepresentativeMeetingBigNumberSchema
from apps.web_sockets.signals import signal_meeting_detail, update_representative_meeting_detail


class MeetingDetail(Schema):
    serializer = MeetingSchema
    channel = 'meeting_detail'
    filter_key = 'id'
    type = 'object'
    signals = [signal_meeting_detail]
    is_priority = True
    identifier = 'meeting_detail'

    def get_room(self):
        return self.instance.id

    def filter(self):
        return {self.filter_key: self.instance.id}


class RepresentativeDetail(Schema):
    serializer = RepresentativeMeetingBigNumberSchema
    channel = 'representatives_meeting_list'
    filter_key = 'meeting_id'
    send_initial = False
    signals = [post_save, update_representative_meeting_detail]
    many = False
    only_initial = False
    type = 'array_update'

    def get_room(self):
        return self.instance.meeting.id

    def filter(self):
        return {self.filter_key: self.instance.meeting.id}


class ClasseSocket(Schema):
    serializer = ClasseSchema
    channel = 'classe_list'
    many = True
    type = 'array'
    send_initial = True
    filter_key = None

    def get_room(self):
        return 'general_intranet'

    @classmethod
    def get_filters(cls, room_id):
        return {}

    def filter(self):
        return {}