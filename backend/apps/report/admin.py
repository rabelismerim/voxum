from django.contrib import admin

from apps.report.models import ReportMeeting, ReportVoting
from core.abstract.admin import AbstractAdmin


@admin.register(ReportMeeting)
class ReportMeetingAdmin(AbstractAdmin):
    actions = ['rerun_task']

    def rerun_task(self, request, queryset):
        for report in queryset:
            report.run_task()


@admin.register(ReportVoting)
class ReportVotingAdmin(AbstractAdmin):
    actions = ['rerun_task']

    def rerun_task(self, request, queryset):
        for report in queryset:
            report.run_task()