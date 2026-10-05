from apps.voxum_base.views_sockets import AbstractMeetingSocket, Schema, SchemaGeneral
from core.permissions.views import CheckUserVotingPermissionSockets


class MeetingSocket(AbstractMeetingSocket):
    current_protocol = 'V2'
    schema = Schema
    channel_layer_alias = 'intranet'
    permission_classes = [CheckUserVotingPermissionSockets]


class GeneralSocket(AbstractMeetingSocket):
    current_protocol = 'V2'
    schema = SchemaGeneral
    channel_layer_alias = 'general_intranet'
    permission_classes = [CheckUserVotingPermissionSockets]

    def get_room(self):
        return 'general_intranet'

    def get_meeting_id(self):
        return 'general_intranet'

    async def send_user_connected(self):
        """Signal para indicação de User conectado"""
        pass

    async def send_user_disconnected(self):
        """Signal para indicação de User desconectado"""
        pass