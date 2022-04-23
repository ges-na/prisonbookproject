import datetime

from django.contrib import admin
from django.db.models import F
from .models import Inmate, Prison

@admin.action(description='batch update date sent')
def update_package_sent(modeladmin, request, queryset):
    now = datetime.datetime.now()
    queryset.update(last_sent=now, pending_letter=None, package_count=F('package_count') + 1)


class InmateAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'inmate_number', 'current_prison', 'last_sent', 'package_count', 'pending_letter')
    list_filter = ('prisons__prison',)
    search_fields = ('inmate_number', 'last_name')
    actions = (update_package_sent,)

    def current_prison(self, inmate):
        return inmate.current_prison


class PrisonAdmin(admin.ModelAdmin):
    pass

admin.site.register(Inmate, InmateAdmin)
admin.site.register(Prison, PrisonAdmin)
