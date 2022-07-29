import datetime
import json

from django.contrib import admin
from django.db.models import F
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export import widgets
from reversion.admin import VersionAdmin
from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add

from .models import Person, Prison, Letter, PersonPrison, WorkflowStage

#probably only good for testing
@admin.action(description='Mark selected letters as Processed')
def move_to_processed(modeladmin, request, queryset):
    now = datetime.datetime.now()
    queryset.update(awaiting_fulfillment_date=None, fulfilled_date=None, workflow_stage=WorkflowStage.PROCESSED)

#should this blank fulfilled_date?
@admin.action(description='Mark selected letters as Awaiting Fulfillment')
def move_to_awaiting_fulfillment(modeladmin, request, queryset):
    now = datetime.datetime.now()
    queryset.update(awaiting_fulfillment_date=now, fulfilled_date=None, workflow_stage=WorkflowStage.AWAITING_FULFILLMENT)

@admin.action(description='Mark selected letters as Fulfilled')
def move_to_fulfilled(modeladmin, request, queryset):
    now = datetime.datetime.now()
    for obj in queryset:
        obj.person.package_count + 1
        obj.save()
    queryset.update(fulfilled_date=now, workflow_stage=WorkflowStage.FULFILLED)


class PersonResource(resources.ModelResource):
    legacy_last_served_date = Field(attribute='legacy_last_served_date', column_name='legacy_last_served_date', widget=widgets.DateWidget(format='%m/%d/%Y'))

    class Meta:
        model = Person
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'inmate_number', 'last_name', 'first_name', 'legacy_prison_id', 'legacy_last_served_date')

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        row_data = json.loads(dataset.get_json())
        for row in row_data:
            person_id = row["id"]
            legacy_prison_id = row["legacy_prison_id"]
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


class PrisonResource(resources.ModelResource):
    class Meta:
        model = Prison
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'name', 'prison_type', 'legacy_id', 'street_address', 'city', 'state', 'zipcode', 'notes')


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

    list_display = ('id', 'inmate_number', 'last_name', 'first_name', 'eligibility', 'last_served', 'current_prison', 'package_count', 'pending_letter_count', 'letter_count',)
    readonly_fields = ('current_prison',)
    # list_filter = ('prisons__prison',)
    search_fields = ('inmate_number', 'last_name', 'first_name',)
    list_display_links = ('first_name', 'last_name', 'id',)
    readonly_fields = ('created_by', 'modified_by', 'created_date', 'modified_date',)
    inlines = [PersonPrisonInline]

    def current_prison(self, person):
        if not person.current_prison:
            return
        link = reverse("admin:app_prison_change", kwargs={"object_id": person.current_prison.id})
        return format_html(f"<a href={link}>{person.current_prison.name}</a>")

    current_prison.allow_tags = True

    # This is fragile due to workflow_stage__in
    def pending_letter_count(self, person):
        if not person.pending_letter_count:
            return
        return format_html(f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}&workflow_stage__in=processed,awaiting_fulfillment>{person.pending_letter_count}</a>")

    def letter_count(self, person):
        if not person.letter_count:
            return
        return format_html(f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}>{person.letter_count}</a>")


@admin.register(Prison)
class PrisonAdmin(ImportExportModelAdmin, VersionAdmin):
    resource_class = PrisonResource

    list_display = ('id', 'name', 'prison_type', 'street_address', 'restrictions', 'notes',)
    list_display_links = ('name',)


@admin.register(Letter)
class LetterAdmin(VersionAdmin):
    list_display = ('id', 'person', 'workflow_stage', 'postmark_date', 'processed_date', 'awaiting_fulfillment_date', 'fulfilled_date', 'eligibility', 'created_by',)
    list_filter = ('workflow_stage',)
    list_display_links = ('id',)
    readonly_fields = ('created_date', 'modified_date', 'created_by',)
    fields = ('person', 'workflow_stage', 'postmark_date', 'processed_date', 'created_date', 'modified_date',)
    actions = (move_to_awaiting_fulfillment, move_to_fulfilled, move_to_processed,)

    def eligibility(self, letter):
        return letter.person.eligibility

    form = make_ajax_form(Letter, {
        'person':'person'
        })

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        autoselect_fields_check_can_add(form, self.model, request.user)
        return form

# class PrisonField(Field):
#     def save(self, obj, data, **kwargs):
#         kwargs.pop('is_m2m', None)
#         cleaned = self.clean(data, **kwargs)
