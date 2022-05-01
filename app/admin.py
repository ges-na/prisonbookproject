import datetime

from django.contrib import admin
from django.db.models import F
from django.forms import ModelForm

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from .models import Person, Prison, Letter, PersonPrison

@admin.action(description='batch update date sent')
def update_package_sent(modeladmin, request, queryset):
    now = datetime.datetime.now()
    queryset.update(last_sent=now, pending_letter=None, package_count=F('package_count') + 1)


class PersonResource(resources.ModelResource):

    class Meta:
        model = Person
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'inmate_number', 'last_name', 'first_name',
                'last_sent', 'package_count', 'pending_letter', 'eligibility',)


class PersonPrisonForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PersonPrisonForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['prison'].disabled = True


class PersonPrisonInline(admin.TabularInline):
    model = PersonPrison
    extra = 0
    can_delete = False
    fields = ('prison', 'current',)
    form = PersonPrisonForm

@admin.register(Person)
class PersonAdmin(VersionAdmin, ImportExportModelAdmin):
    resource_class = PersonResource

    list_display = ('id', 'inmate_number', 'last_name', 'first_name', 'last_sent', 'package_count', 'pending_letter', 'eligibility', 'current_prison', 'created_by', 'created_date', 'modified_by', 'modified_date',)
    readonly_fields = ('current_prison',)
    list_filter = ('prisons__prison',)
    search_fields = ('inmate_number', 'last_name', 'first_name',)
    actions = (update_package_sent,)
    list_display_links = ('first_name', 'last_name', 'id')
    readonly_fields = ('created_by', 'modified_by', 'created_date', 'modified_date',)
    inlines = [PersonPrisonInline]

    def current_prison(self, person):
        return person.current_prison


@admin.register(Prison)
class PrisonAdmin(VersionAdmin):
    list_display = ('id', 'name', 'prison_type', 'restrictions', 'notes',)
    list_display_links = ('name',)


@admin.register(Letter)
class LetterAdmin(VersionAdmin):
    pass
