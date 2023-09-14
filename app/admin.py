from datetime import datetime

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from django.contrib import admin
from django.forms import ModelForm, forms, BooleanField
from django.urls import reverse
from django.utils.timezone import make_aware
from django.utils.html import format_html
from import_export import resources, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from .models import (
    Letter,
    Person,
    PersonPrison,
    Prison,
    WorkflowStage,
    PrisonTypes,
)


# probably only good for testing, might turn off later
@admin.action(description="Mark selected letters as Stage 1 Complete")
def move_to_stage1_complete(modeladmin, request, queryset):
    queryset.update(
        fulfilled_date=None,
        workflow_stage=WorkflowStage.STAGE1_COMPLETE,
    )


# turned off in form, only available via admin actions
@admin.action(description="Mark selected letters as Fulfilled")
def move_to_fulfilled(modeladmin, request, queryset):
    now = datetime.now()
    for letter in queryset:
        letter.prison_sent_to = letter.person.current_prison
        letter.save()
    queryset.update(fulfilled_date=now, workflow_stage=WorkflowStage.FULFILLED)


# @admin.action(
#     description="Mark selected letters as Fulfilled, provide specific date to apply"
# )
# def move_to_fulfilled_backdated(modeladmin, request, queryset):
#     for obj in queryset:
#         obj.person.package_count + 1
#         obj.save()
#     queryset.update(
#         fulfilled_date=request.selected_date, workflow_stage=WorkflowStage.FULFILLED
#     )


class PersonResource(resources.ModelResource):
    current_prison = Field(attribute="current_prison")
    last_served = Field(attribute="last_served")
    eligibility = Field(attribute="eligibility")
    package_count = Field(attribute="package_count")
    letter_count = Field(attribute="letter_count")
    # this causes legacy_last_served_date to be part of the export
    # even though it is probably confusing
    legacy_last_served_date = Field(
        attribute="legacy_last_served_date",
        column_name="legacy_last_served_date",
        widget=widgets.DateTimeWidget(format="%Y-%m-%d %H:%M:%S"),
    )

    class Meta:
        model = Person
        skip_unchanged = True
        report_skipped = True
        fields = (
            "id",
            "inmate_number",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
            "legacy_last_served_date",
            "legacy_prison_id",
        )
        readonly_fields = (
            "current_prison",
            "last_served",
            "eligibility",
            "letter_count",
            "package_count",
        )
        export_order = (
            "id",
            "last_name",
            "middle_name",
            "first_name",
            "name_suffix",
            "status",
            "current_prison",
            "last_served",
            "eligibility",
            "letter_count",
            "package_count",
        )

    def after_save_instance(self, instance, using_transactions, dry_run):
        if instance.legacy_prison_id is None:
            return
        legacy_prison_id = instance.legacy_prison_id
        prison = Prison.objects.filter(legacy_id=legacy_prison_id).first()
        if not prison:
            raise Exception(f"Prison with legacy id {legacy_prison_id} not found!")
        existing_records = PersonPrison.objects.filter(person_id=instance.id).count()
        if existing_records > 0:
            return
        PersonPrison.objects.create(person_id=instance.id, prison_id=prison.id)


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
            "additional_mailing_headers",
            "mailing_city",
            "mailing_state",
            "mailing_zipcode",
            "restrictions",
            "notes",
        )


class PersonPrisonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonPrisonForm, self).__init__(*args, **kwargs)


class PersonPrisonInline(admin.TabularInline):
    model = PersonPrison
    max_num = 1
    can_delete = False
    verbose_name = "Prison"
    verbose_name_plural = "Prisons"
    fields = ("prison",)
    form = PersonPrisonForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prison":
            kwargs["queryset"] = Prison.objects.all().order_by("name")
        return super(PersonPrisonInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override the formset function in order to remove the add and
        change buttons beside the foreign key pull-down menus in the inline.
        From: https://stackoverflow.com/a/37558444
        """
        formset = super(PersonPrisonInline, self).get_formset(request, obj, **kwargs)
        form = formset.form
        widget = form.base_fields["prison"].widget
        widget.can_add_related = False
        widget.can_change_related = False
        return formset


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

    def last_served_date(self, obj):
        if obj.last_served:
            return obj.last_served.strftime("%Y-%m-%d")

    list_display = (
        "inmate_number",
        "last_name",
        "first_name",
        "eligibility",
        "status",
        "last_served_date",
        "current_prison",
        "package_count",
        "pending_letter_count",
        "letter_count",
        "created_by",
        "created_date",
        "modified_date",
    )
    readonly_fields = (
        "current_prison",
        "created_by",
        "created_date",
        "modified_date",
        "eligibility",
        "package_count",
        "pending_letter_count",
        "letter_count",
    )
    list_filter = (
        # "prisons__prison",
        # EligibilityListFilter,
    )
    search_fields = (
        "inmate_number",
        "last_name",
        "first_name",
    )
    list_display_links = (
        "first_name",
        "last_name",
    )
    fields = (
        "inmate_number",
        "eligibility",
        "last_name",
        "middle_name",
        "first_name",
        "name_suffix",
        "pending_letter_count",
        "status",
        "notes",
    )
    list_per_page = 25
    inlines = [PersonPrisonInline]

    def current_prison(self, person):
        if not person.current_prison:
            return
        link = reverse(
            "admin:app_prison_change", kwargs={"object_id": person.current_prison.id}
        )
        return format_html(f"<a href={link}>{person.current_prison.name}</a>")

    current_prison.allow_tags = True

    def pending_letter_count(self, person):
        if not person.pending_letter_count:
            return
        return format_html(
            f"<a href={reverse('admin:app_letter_changelist')}?person={person.id}&workflow_stage__in={WorkflowStage.STAGE1_COMPLETE} target='_blank'>{person.pending_letter_count}</a>"
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
        obj.modified_date = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Prison)
class PrisonAdmin(ImportExportModelAdmin):
    resource_class = PrisonResource

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
        "additional_mailing_headers",
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
        if prison.additional_mailing_headers:
            return format_html(
                f"{prison.name}<br/>{prison.additional_mailing_headers}<br/>{prison.mailing_address}<br/>{prison.mailing_city}, {prison.mailing_state} {prison.mailing_zipcode}"
            )
        return format_html(
            f"{prison.name}<br/>{prison.mailing_address}<br/>{prison.mailing_city}, {prison.mailing_state} {prison.mailing_zipcode}"
        )

    display_mailing_address.allow_tags = True
    display_mailing_address.short_description = "Mailing Address"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.modified_date = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Letter)
class LetterAdmin(ImportExportModelAdmin):

    list_display = (
        "letter_name",
        "workflow_stage",
        "postmark_date",
        "eligibility",
        "person_current_prison",
        "stage1_complete_date",
        "fulfilled_date",
        "prison_sent_to_list_display",
        "prison_mailing_address",
        "person_list_display",
        "created_by",
        "created_date",
        "modified_date",
    )
    list_filter = ("workflow_stage", "prison_sent_to")
    list_display_links = ("letter_name",)
    search_fields = (
        "person__last_name",
        "person__first_name",
        "person__inmate_number",
    )
    readonly_fields = (
        "created_date",
        "created_by",
        "stage1_complete_date",
    )
    fields = (
        "person",
        "postmark_date",
        "stage1_complete_date",
        "workflow_stage",
        "counts_against_last_served",
        "notes",
    )
    actions = (
        move_to_fulfilled,
        move_to_stage1_complete,
    )

    def check_to_keep_at_stage1_complete(self):
        pass

    def letter_name(self, letter):
        return f"{letter.person.inmate_number} | {letter.person.last_name}, {letter.person.first_name} - {letter.postmark_date}"

    def person_list_display(self, letter):
        if not letter.person:
            # This is a problem, do something smarter here
            return
        link = reverse(
            "admin:app_person_change", kwargs={"object_id": letter.person.id}
        )
        return format_html(f"<a href={link}>{letter.person.last_name}</a>")

    person_list_display.allow_tags = True
    person_list_display.admin_order_field = "person__last_name"
    person_list_display.short_description = "Person"

    def person_current_prison(self, letter):
        return letter.person.current_prison

    def prison_sent_to_list_display(self, letter):
        if not letter.prison_sent_to:
            return
        link = reverse(
            "admin:app_prison_change", kwargs={"object_id": letter.prison_sent_to.id}
        )
        return format_html(f"<a href={link}>{letter.prison_sent_to}</a>")

    prison_sent_to_list_display.allow_tags = True
    prison_sent_to_list_display.admin_order_field = "prison__name"
    prison_sent_to_list_display.short_description = "Prison Sent To"

    # TODO: this is so gross
    def prison_mailing_address(self, letter):
        if not letter.person.current_prison:
            return
        if letter.person.current_prison.prison_type == PrisonTypes.SCI:
            return
        curr_prison = letter.person.current_prison
        # this suppresses county/city ID numbers, which is imperfect but accounts for constructed IDs; however, some county prisons do have IDs
        if curr_prison.prison_type == (PrisonTypes.COUNTY or PrisonTypes.CITY):
            return format_html(
                f"{letter.person.first_name} {letter.person.last_name}<br/>{curr_prison.name}<br/>{curr_prison.mailing_address}<br/>{curr_prison.mailing_city}, {curr_prison.mailing_state} {curr_prison.mailing_zipcode}"
            )
        if curr_prison.additional_mailing_headers:
            return format_html(
                f"{letter.person.first_name} {letter.person.last_name}<br/>{letter.person.inmate_number}<br/>{curr_prison.name}<br/>{curr_prison.additional_mailing_headers}<br/>{curr_prison.mailing_address}<br/>{curr_prison.mailing_city}, {curr_prison.mailing_state} {curr_prison.mailing_zipcode}"
            )
        return format_html(
            f"{letter.person.first_name} {letter.person.last_name}<br/>{letter.person.inmate_number}<br/>{curr_prison.name}<br/>{curr_prison.mailing_address}<br/>{curr_prison.mailing_city}, {curr_prison.mailing_state} {curr_prison.mailing_zipcode}"
        )

    prison_mailing_address.allow_tags = True
    prison_mailing_address.short_description = "Non-SCI address"

    def eligibility(self, letter):
        return letter.person.eligibility

    form = make_ajax_form(Letter, {"person": "person"})

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[
            "counts_against_last_served"
        ].label = "Counts toward the person's last served date. (Only uncheck for survey response packages.)"
        autoselect_fields_check_can_add(form, self.model, request.user)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_date = datetime.now()
        super().save_model(request, obj, form, change)
