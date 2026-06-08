from datetime import datetime
from typing import TYPE_CHECKING

from ajax_select import make_ajax_field
from django.contrib import admin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from src.app.models.issue import LetterIssue, PersonIssue

if TYPE_CHECKING:
    pass


class PersonIssueAdminForm(ModelForm):
    class Meta:
        model = PersonIssue
        fields = ("person", "issue", "additional_note", "resolved", "resolved_note")

    person = make_ajax_field(PersonIssue, "person", "person_channel")


class LetterIssueAdminForm(ModelForm):
    class Meta:
        model = LetterIssue
        fields = ("letter", "issue", "additional_note", "resolved", "resolved_note")

    letter = make_ajax_field(LetterIssue, "letter", "letter_channel")


class IssueAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    base_list_display = (
        "resolved",
        "issue",
        "additional_note",
        "resolved_note",
        "resolved_by",
        "resolved_date",
        "last_updated_by",
        "last_updated_date",
        "created_date",
        "created_by",
    )

    ordering = (
        "resolved",
        "-modified_date",
    )
    list_display_links = ("issue",)
    list_filter = ("issue", "resolved")

    def last_updated_date(self, issue: PersonIssue):
        return issue.modified_date if issue.modified_date else issue.created_date

    def last_updated_by(self, issue: PersonIssue):
        return issue.modified_by if issue.modified_by else issue.created_by

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.modified_date = datetime.now()
        if "resolved" in form.changed_data and obj.resolved:
            obj.resolved_by = request.user
            obj.resolved_date = datetime.now()
        super().save_model(request, obj, form, change)


class PersonIssueAdmin(IssueAdmin):
    form = PersonIssueAdminForm
    list_display = ["person_list_display", *IssueAdmin.base_list_display]
    search_fields = (
        "person__last_name",
        "person__first_name",
        "person__inmate_number",
        "person__id",
    )

    def person_list_display(self, issue: PersonIssue):
        link = reverse("admin:app_person_change", kwargs={"object_id": issue.person.id})
        return format_html("<a href={}>{}</a>", link, issue.person.__str__())

    setattr(person_list_display, "short_description", "Person")


class LetterIssueAdmin(IssueAdmin):
    form = LetterIssueAdminForm
    list_display = ["letter_list_display", *IssueAdmin.base_list_display]
    search_fields = (
        "letter__id",
        "letter__person__first_name",
        "letter__person__last_name",
        "letter__person__inmate_number",
        "letter__postmark_date",
    )

    def letter_list_display(self, issue: LetterIssue):
        link = reverse("admin:app_letter_change", kwargs={"object_id": issue.letter.id})
        return format_html("<a href={}>{}</a>", link, issue.letter.__str__())

    setattr(letter_list_display, "short_description", "Letter")


class IssueInline(admin.TabularInline):
    class Meta:
        abstract = True

    verbose_name = "Issue"
    can_delete = False
    min_num = 0
    extra = 0
    fields = ("issue", "additional_note")
    show_change_link = True
    can_delete = False


class PersonIssueInline(IssueInline):
    model = PersonIssue

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "issue":
            kwargs["choices"] = [("", "-----"), *PersonIssue.IssueTypes.choices]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class LetterIssueInline(IssueInline):
    model = LetterIssue

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "issue":
            kwargs["choices"] = [("", "-----"), *LetterIssue.IssueTypes.choices]
        return super().formfield_for_choice_field(db_field, request, **kwargs)
