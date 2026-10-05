from django.contrib import admin

from apps.recovering.models import Recovering


class RecoveringAdmin(admin.ModelAdmin):
    pass


admin.site.register(Recovering, RecoveringAdmin)