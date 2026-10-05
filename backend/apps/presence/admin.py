from core.abstract.admin import AbstractAdmin
from django.contrib import admin

from apps.presence.models import Presence, PresenceRepresentative


class PresenceAdmin(AbstractAdmin):
    pass


@admin.register(PresenceRepresentative)
class PresenceRepresentativeAdmin(AbstractAdmin):
    pass


admin.site.register(Presence, PresenceAdmin)