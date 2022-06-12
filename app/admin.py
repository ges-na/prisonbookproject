import datetime
import json

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

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        row_data = json.loads(dataset.get_json())
        for row in row_data:
            person_id = row["id"]
            legacy_prison_id = row["prison"]
            prison = Prison.objects.filter(legacy_id=legacy_prison_id).first()
            if not prison:
                raise Exception(f"Prison with legacy id {legacy_prison_id} not found!")
            existing = PersonPrison.objects.filter(person_id=person_id, prison_id=prison.id).first()
            if existing and existing.current:
                continue
            elif existing:
                existing.current = True
                PersonPrison.objects.filter(person_id=person_id).update(current=False)
                existing.save()
                continue
            PersonPrison.objects.create(person_id=person_id, prison_id=prison.id, current=True)

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
class PersonAdmin(ImportExportModelAdmin, VersionAdmin):
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


# class PrisonField(Field):
#     def save(self, obj, data, **kwargs):
#         kwargs.pop('is_m2m', None)
#         cleaned = self.clean(data, **kwargs)
