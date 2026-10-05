from apps.voxum_base.views_sockets import AbstractMeetingSocket, SchemaGuest
from core.permissions.views import CheckGuestUserMeetingPermissionSockets


class MeetingGuestSocket(AbstractMeetingSocket):
    schema = SchemaGuest
    only_admin = False
    channel_layer_alias = 'guest'
    permission_classes = [CheckGuestUserMeetingPermissionSockets]

    def get_room(self):
        return f'{self.get_meeting_id()}__{self.user.id}'
