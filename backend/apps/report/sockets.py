from django.db.models.signals import post_save, post_delete

from apps.voxum_base.views_sockets import SchemaGeneral
from apps.report.schemas import ReportSchema, ReportVotingSchema


class ReportMeetingSocket(SchemaGeneral):
    serializer = ReportSchema
    channel = 'report_meeting_list'
    many = True
    signals = [post_save, post_delete]
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


class ReportVotingSocket(SchemaGeneral):
    serializer = ReportVotingSchema
    channel = 'report_voting_list'
    many = True
    signals = [post_save, post_delete]
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