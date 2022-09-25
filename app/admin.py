import datetime

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from django.contrib import admin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from .models import Letter, Person, PersonPrison, Prison, WorkflowStage


# probably only good for testing
@admin.action(description="Mark selected letters as Stage 1 Complete")
def move_to_stage1_complete(modeladmin, request, queryset):
    queryset.update(
        awaiting_fulfillment_date=None,
        fulfilled_date=None,
        workflow_stage=WorkflowStage.STAGE1_COMPLETE,
    )


# should this blank fulfilled_date?
@admin.action(description="Mark selected letters as Awaiting Fulfillment")
def move_to_awaiting_fulfillment(modeladmin, request, queryset):
    now = datetime.datetime.now()
    queryset.update(
        awaiting_fulfillment_date=now,
        fulfilled_date=None,
        workflow_stage=WorkflowStage.AWAITING_FULFILLMENT,
    )


@admin.action(description="Mark selected letters as Fulfilled")
def move_to_fulfilled(modeladmin, request, queryset):
    now = datetime.datetime.now()
    for obj in queryset:
        obj.person.package_count + 1
        obj.save()
    queryset.update(fulfilled_date=now, workflow_stage=WorkflowStage.FULFILLED)


class PersonResource(resources.ModelResource):
    legacy_last_served_date = Field(
        attribute="legacy_last_served_date",
        column_name="legacy_last_served_date",
        widget=widgets.DateWidget(format="%m/%d/%Y"),
    )

    class Meta:
        model = Person
        skip_unchanged = True
        report_skipped = True
        fields = (
            "id",
            "inmate_number",
            "last_name",
            "first_name",
            "legacy_prison_id",
            "legacy_last_served_date",
        )

    def after_save_instance(self, instance, using_transactions, dry_run):
        legacy_prison_id = instance.legacy_prison_id
        prison = Prison.objects.filter(legacy_id=legacy_prison_id).first()
        if not prison:
            raise Exception(f"Prison with legacy id {legacy_prison_id} not found!")
        existing = PersonPrison.objects.filter(
            person_id=instance.id, prison_id=prison.id
        ).first()
        if existing and existing.current:
            return
        elif existing:
            existing.current = True
            # PersonPrison.objects.filter(person_id=instance.id).update(current=False)
            existing.save()
            return
        PersonPrison.objects.create(
            person_id=instance.id, prison_id=prison.id, current=True
        )


class PrisonResource(resources.ModelResource):
    class Meta:
        model = Prison
        skip_unchanged = True
        report_skipped = True
        fields = (
            "id",
            "name",
            "prison_type",
            "legacy_id",
            "legacy_address",
            "mailing_address",
            "mailing_city",
            "mailing_state",
            "mailing_zipcode",
            "restrictions",
            "notes",
        )


class PersonPrisonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonPrisonForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["prison"].disabled = True


class PersonPrisonInline(admin.TabularInline):
    model = PersonPrison
    extra = 0
    can_delete = False
    fields = ("prison", "current")
    form = PersonPrisonForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prison":
            kwargs["queryset"] = Prison.objects.all().order_by("name")
        return super(PersonPrisonInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class PersonForm(ModelForm):
    def clean_inmate_number(self):
        cleaned_inmate_num = "".join(
            list(filter(str.isalnum, self.cleaned_data["inmate_number"]))
        )
        self.cleaned_data["inmate_number"] = cleaned_inmate_num.upper()
        return self.cleaned_data["inmate_number"]

    def clean_first_name(self):
        self.cleaned_data["first_name"] = self.cleaned_data["first_name"].upper()
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        self.cleaned_data["last_name"] = self.cleaned_data["last_name"].upper()
        return self.cleaned_data["last_name"]


@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    resource_class = PersonResource

    form = PersonForm

    list_display = (
        "id",
        "inmate_number",
        "last_name",
        "first_name",
        "eligibility",
        "status",
        "last_served",
        "current_prison",
        "package_count",
        "pending_letter_count",
        "letter_count",
        "created_by",
        "created_date",
        "modified_date",
    )
    readonly_fields = ("current_prison",)
    # list_filter = ('prisons__prison',)
    search_fields = (
        "inmate_number",
        "last_name",
        "first_name",
    )
    list_display_links = (
        "first_name",
        "last_name",
        "id",
    )
    readonly_fields = (
        "created_by",
        "created_date",
        "modified_date",
        "eligibility",
        "package_count",
        "pending_letter_count",
        "letter_count",
    )
    fields = (
        "inmate_number",
        "eligibility",
        "last_name",
        "first_name",
        "package_count",
        "pending_letter_count",
        "letter_count",
        "status",
    )
    inlines = [PersonPrisonInline]

    def current_prison(self, person):
        if not person.current_prison:
            return
        link = reverse(
            "admin:app_prison_change", kwargs={"object_id": person.current_prison.id}
        )
        return format_html(f"<a href={link}>{person.current_prison.name}</a>")

    current_prison.allow_tags = True

    # This is fragile due to workflow_stage__in
    def pending_letter_count(self, person):
        if not person.pending_letter_count:
            return
        return format_html(
            f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}&workflow_stage__in={WorkflowStage.STAGE1_COMPLETE},{WorkflowStage.AWAITING_FULFILLMENT}>{person.pending_letter_count}</a>"
        )

    def letter_count(self, person):
        if not person.letter_count:
            return
        return format_html(
            f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}>{person.letter_count}</a>"
        )

    def package_count(self, person):
        if not person.package_count:
            return
        return format_html(
            f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}&workflow_stage__in={WorkflowStage.FULFILLED}>{person.package_count}</a>"
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_date = datetime.datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Prison)
class PrisonAdmin(ImportExportModelAdmin):
    resource_class = PrisonResource

    # All mail goes through Security Processing Center, addresses suppressed
    list_display = (
        "id",
        "name",
        "prison_type",
        "display_mailing_address",
        "restrictions",
        "notes",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
    )
    list_display_links = ("name",)
    list_filter = ("prison_type",)
    search_fields = (
        "name",
        "notes",
        "restrictions",
    )
    fields = (
        "name",
        "prison_type",
        "mailing_address",
        "mailing_city",
        "mailing_state",
        "mailing_zipcode",
        "legacy_address",
        "restrictions",
        "notes",
    )

    def display_mailing_address(self, prison):
        if not prison.mailing_address:
            return
        return format_html(
            f"{prison.name}<br/>{prison.mailing_address}<br/>{prison.mailing_city}, {prison.mailing_state} {prison.mailing_zipcode}"
        )

    display_mailing_address.allow_tags = True
    display_mailing_address.short_description = "Mailing Address"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.modified_date = datetime.datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Letter)
class LetterAdmin(ImportExportModelAdmin):
    list_display = (
        "letter_name",
        "person_list_display",
        "workflow_stage",
        "postmark_date",
        "stage1_complete_date",
        "awaiting_fulfillment_date",
        "fulfilled_date",
        "prison_mailing_address",
        "eligibility",
        "created_by",
        "created_date",
        "modified_date",
    )
    list_filter = ("workflow_stage",)
    list_display_links = ("letter_name",)
    search_fields = (
        "person__last_name",
        "person__first_name",
        "person__inmate_number",
    )
    readonly_fields = (
        "created_date",
        "created_by",
    )
    fields = (
        "person",
        "workflow_stage",
        "postmark_date",
        "stage1_complete_date",
        "created_date",
    )
    actions = (
        move_to_awaiting_fulfillment,
        move_to_fulfilled,
        move_to_stage1_complete,
    )

    def letter_name(self, letter):
        return f"{letter.person.last_name}, {letter.person.first_name} - {letter.postmark_date}"

    def person_list_display(self, letter):
        if not letter.person:
            # This is a problem, do something smarter here
            return
        link = reverse(
            "admin:app_person_change", kwargs={"object_id": letter.person.id}
        )
        return format_html(f"<a href={link}>{letter.person.last_name}</a>")

    person_list_display.allow_tags = True
    person_list_display.short_description = "Person"

    def prison_mailing_address(self, letter):
        if not letter.person.current_prison:
            return
        curr_prison = letter.person.current_prison
        # TODO: this will probably insert another line break if no additional_mailing_headers, which there are not many; fix
        return format_html(
            f"{letter.person.first_name} {letter.person.last_name}<br/>{letter.person.inmate_number}<br/>{curr_prison.name}<br/>{curr_prison.additional_mailing_headers}<br/>{curr_prison.mailing_address}<br/>{curr_prison.mailing_city}, {curr_prison.mailing_state} {curr_prison.mailing_zipcode}"
        )

    prison_mailing_address.allow_tags = True

    def eligibility(self, letter):
        return letter.person.eligibility

    form = make_ajax_form(Letter, {"person": "person"})

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        autoselect_fields_check_can_add(form, self.model, request.user)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_date = datetime.datetime.now()
        super().save_model(request, obj, form, change)
