from django.contrib import admin

from apps.voxum_base.admin import AbstractAdmin
from apps.creditor.models import Representative, Creditor


class CreditorAdmin(AbstractAdmin):
    list_display = ('credit_value', 'classe', 'meeting_invited', 'online', 'is_deleted', 'doc_ok')
    readonly_fields = ('legal_number', 'code')
    list_filter = ('meeting_invited', 'online', 'is_deleted', 'doc_ok')
    search_fields = (
        'guest__user__first_name__icontains', 'guest__user__last_name__icontains', 'guest__user__email__icontains',
        'guest__entity__legal_number__icontains',)

    def get_queryset(self, request):
        qs = self.model.objects_admin.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class RepresentativeAdmin(AbstractAdmin):
    list_display = ('creditor', 'representative_meeting', 'is_deleted')
    readonly_fields = ('legal_number',)
    list_filter = ('online', 'is_deleted')

    search_fields = (
        'representative__guest__user__first_name__icontains', 'representative__guest__user__last_name__icontains',
        'representative__guest__user__email__icontains',
        'representative__guest__entity__legal_number__icontains',

        'creditor__guest__user__first_name__icontains', 'creditor__guest__user__last_name__icontains',
        'creditor__guest__user__email__icontains',
        'creditor__guest__entity__legal_number__icontains'
    )

    def representative_meeting(self, obj):
        return obj.representative.meeting

    def get_queryset(self, request):
        qs = self.model.objects_admin.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(Creditor, CreditorAdmin)
admin.site.register(Representative, RepresentativeAdmin)