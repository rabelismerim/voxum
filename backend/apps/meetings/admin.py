"""
Registra os modelos da aplicação Meeting no site de administração do Django.
"""
from core.abstract.admin import AbstractAdmin
from django.contrib import admin

from apps.guest.tasks import SendInvitationLinkCiamTask, SendMeetingLinkTask
from apps.meetings.models import Meeting, Classe, RepresentativeMeeting, UserMeeting, MeetingGroup


@admin.register(Meeting)
class MeetingAdmin(AbstractAdmin):
    readonly_fields = ['meeting_reference', 'meeting_group', 'order', 'situation']
    actions = ['send_invitation_link_ciam', 'send_invitation_link_meeting', 'force_send_invitation_link_meeting']

    def send_invitation_link_ciam(self, request, queryset):
        for meeting in queryset:
            SendInvitationLinkCiamTask.delay(meeting.id)

    def send_invitation_link_meeting(self, request, queryset):
        self._send_meeting(request, queryset, force=False)

    def force_send_invitation_link_meeting(self, request, queryset):
        self._send_meeting(request, queryset, force=True)

    def _send_meeting(self, request, queryset, force):
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        for meeting in queryset:
            link = f'{protocol}://{host}/voxum/guest/{meeting.id}/'
            SendMeetingLinkTask.delay(link, meeting.id, force)


@admin.register(Classe)
class ClasseAdmin(AbstractAdmin):
    pass


@admin.register(RepresentativeMeeting)
class RepresentativeMeetingAdmin(AbstractAdmin):
    list_display = ['meeting', 'doc_ok']
    list_filter = ('doc_ok',)


@admin.register(UserMeeting)
class UserMeetingAdmin(AbstractAdmin):
    pass


@admin.register(MeetingGroup)
class MeetingGroupAdmin(AbstractAdmin):
    pass