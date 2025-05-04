from datetime import datetime

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from app.models.letter import Letter
from app.models.person import WorkflowStage
from app.models.prison import Prison


# probably only good for testing, might turn off later
@admin.action(description="Mark selected letters as Stage 1 Complete")
def move_to_stage1_complete(modeladmin, request, queryset):
    queryset.update(
        fulfilled_date=None,
        workflow_stage=WorkflowStage.STAGE1_COMPLETE,
    )


# WorkflowStage.FULFILLED turned off in form, only available via this admin action
@admin.action(description="Mark selected letters as Fulfilled")
def move_to_fulfilled(modeladmin, request, queryset):
    now = datetime.now()
    for letter in queryset:
        if not letter.person:
            raise Exception(
                f"Letter {letter.id} has no person. There needs to be a letter.person for this operation"
            )
        letter.prison_sent_to = letter.person.current_prison
        letter.save()
    queryset.update(fulfilled_date=now, workflow_stage=WorkflowStage.FULFILLED)


class LetterAdmin(ImportExportModelAdmin):
    list_display = (
        "letter_name",
        "workflow_stage",
        "postmark_date",
        "eligibility",
        "person_current_prison",
        "restrictions",
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

    list_per_page = 50

    def letter_name(self, letter):
        if not letter.person:
            return f"NO PERSON - {letter.postmark_date}"
        return f"{letter.person.inmate_number} | {letter.person.last_name}, {letter.person.first_name} - {letter.postmark_date}"

    def person_list_display(self, letter: Letter):
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

    def person_current_prison(self, letter) -> Prison | None:
        return letter.person.current_prison if letter.person else None

    def restrictions(self, letter):
        if not letter.person:
            return ""
        if letter.person.current_prison:
            return letter.person.current_prison.restrictions

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
        if not letter.person or not letter.person.current_prison:
            return
        if letter.person.current_prison.prison_type == Prison.Types.SCI:
            return
        curr_prison = letter.person.current_prison
        # this suppresses county/city ID numbers, which is imperfect but accounts for constructed IDs; however, some county prisons do have IDs
        if curr_prison.prison_type in (Prison.Types.COUNTY, Prison.Types.CITY):
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

    def eligibility(self, letter: Letter) -> bool:
        return letter.person.eligibility if letter.person else False

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
