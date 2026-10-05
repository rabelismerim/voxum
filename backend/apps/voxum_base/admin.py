import logging

from core.abstract.admin import AbstractAdmin
from config.settings import ENABLE_TOKEN
from django.contrib import admin

try:
    from django.contrib.admin.exceptions import NotRegistered
except ImportError:
    NotRegistered = None
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.db.models import ExpressionWrapper, F, DurationField
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from rest_framework.authtoken.models import TokenProxy
from apps.voxum_base.models import Entity, Coin  # Assumindo nova app 'base'

admin.site.unregister(Group)

if NotRegistered:
    try:
        admin.site.unregister(TaskResult)
    except NotRegistered:
        pass
else:
    try:
        admin.site.unregister(TaskResult)
    except Exception as e:
        logging.debug(e)


@admin.register(TaskResult)
class TaskResultAdmin(TaskResultAdmin, AbstractAdmin):

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = list(self.list_display)
        self.list_display.append('execution_time')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            execution_time=ExpressionWrapper(
                F('date_done') - F('date_created'),
                output_field=DurationField()
            )
        )
        ordering = ['execution_time'] + list(self.get_ordering(request))
        return queryset.order_by(*ordering)

    def execution_time(self, obj):
        if obj.date_done and obj.date_created:
            return (obj.date_done - obj.date_created).total_seconds()
        return 0

    execution_time.admin_order_field = 'execution_time'


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    list_display = ('name', 'id')
    list_filter = ('name',)
    ordering = ('name',)


class EntityAdmin(AbstractAdmin):
    pass


class CoinAdmin(AbstractAdmin):
    pass


if ENABLE_TOKEN:
    admin.site.unregister(TokenProxy)

    @admin.register(TokenProxy)
    class CustomTokenAdmin(AbstractAdmin):
        list_display = ('key', 'user', 'created')
        fields = ('user',)
        ordering = ('-created',)
        readonly_fields = []
        search_fields = ['user']

admin.site.register(Entity, EntityAdmin)
admin.site.register(Coin, CoinAdmin)