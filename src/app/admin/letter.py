from datetime import datetime

from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_field
from django.contrib import admin
from django.forms import ModelForm, ValidationError
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from src.app.models.letter import Letter
from src.app.models.person import WorkflowStage
from src.app.models.prison import Prison
from src.app.utils import render_address_template


class LetterForm(ModelForm):

    person = make_ajax_field(Letter, "person", "person")

    class Meta:
        model = Letter
        fields = ["person", "postmark_date", "stage1_complete_date", "workflow_stage", "counts_against_last_served", "notes"]

    def clean_person(self):
        if person := self.cleaned_data.get("person"):
            if person.current_prison:
                return person
            else:
                raise ValidationError(f"Adding a person to a letter requires that person to have a current_prison. Please add current prison value to {person.inmate_number} {person.full_name} to create/update this letter.")
        raise ValidationError("You must add a person to create or update a letter.")

class LetterAdmin(ImportExportModelAdmin, AjaxSelectAdmin):
    form = LetterForm
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
    list_filter = ("workflow_stage", "prison_sent_to", "fulfilled_date")
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
        "move_to_fulfilled",
        "move_to_stage1_complete",
        "move_to_discarded"
    )

    list_per_page = 50

    def eligibility(self, letter):
        return letter.person.get_eligibility_str()

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
        return format_html("<a href={}>{}</a>", link, letter.person.last_name)

    setattr(person_list_display, "admin_order_field", "person__last_name")
    setattr(person_list_display, "short_description", "Person")

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
        return format_html("<a href={}>{}</a>", link, letter.prison_sent_to)

    @admin.action(description="Mark selected letters as Stage 1 Complete")
    def move_to_stage1_complete(self, request, queryset):
        queryset.update(
            fulfilled_date=None,
            workflow_stage=WorkflowStage.STAGE1_COMPLETE,
        )

    @admin.action(description="Mark selected letters as Fulfilled")
    def move_to_fulfilled(self, request, queryset):
        """
        WorkflowStage.FULFILLED turned off in form, only available via this admin action.
        """
        for letter in queryset:
            if not letter.person:
                link = reverse('admin:app_letter_change', kwargs={"object_id": letter.id})
                self.message_user(request, format_html("Letter <a href={} data-popup='yes'>{} - {}</a> not changed. There needs to be a person assigned to the letter for this operation.", link, letter.id, letter.name))
                continue
            letter.prison_sent_to = letter.person.current_prison
            letter.save()
        queryset.update(fulfilled_date=datetime.now(), workflow_stage=WorkflowStage.FULFILLED)

    @admin.action(description="Mark selected letters as Discarded")
    def move_to_discarded(self, request, queryset):
        for letter in queryset:
            if letter.workflow_stage == WorkflowStage.FULFILLED:
                link = reverse('admin:app_letter_changelist', kwargs={"object_id": letter.id})
                self.message_user(request, format_html("Cannot mark Fulfilled letter as Discarded. Letter <a href={}>{} - {}</a> not changed.", link, letter.id, letter.name))
                continue
        queryset.update(workflow_stage=WorkflowStage.DISCARDED)

    def prison_mailing_address(self, letter: Letter):
        if not letter.person or not letter.person.current_prison:
            return
        if letter.person.current_prison.prison_type == Prison.Types.SCI:
            return
        curr_prison = letter.person.current_prison
        # this suppresses county/city ID numbers (which may be incorrect)
        # unhandled case: some county prisoners do have correct IDs
        if curr_prison.prison_type in (Prison.Types.COUNTY, Prison.Types.CITY):
            inmate_number = None
        else:
            inmate_number = letter.person.inmate_number

        headers = [
            letter.person.get_name_str(),
            inmate_number,
            curr_prison.name,
        ]
        if curr_prison.additional_mailing_headers:
            headers.append(curr_prison.additional_mailing_headers)
        return render_address_template(
            headers,
            curr_prison.mailing_address,
            curr_prison.mailing_city,
            curr_prison.mailing_state,
            curr_prison.mailing_zipcode,
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_date = datetime.now()
        super().save_model(request, obj, form, change)
