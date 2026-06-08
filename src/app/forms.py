from datetime import datetime

from ajax_select import make_ajax_field
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as DjAuthenticationForm,
    PasswordResetForm as DjPasswordResetForm,
)
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.views.decorators.debug import sensitive_variables
from django_registration.forms import RegistrationForm as DjRegistrationForm

from src.app.admin.letter import LetterAdminForm
from src.app.admin.person import PersonAdminForm
from src.app.models.issue import LetterIssue, PersonIssue
from src.app.models.letter import Letter
from src.app.models.person import Person
from src.app.models.prison import PersonPrison, Prison
from src.auth.models import User

# TODO: split into different files
note_field = forms.Textarea(
    attrs={
        "rows": 3,
        "cols": 40,
        "placeholder": "Only fill this out if you need to describe an issue.",
    },
)


class ContribLetterForm(LetterAdminForm):
    class Meta(LetterAdminForm.Meta):
        model = Letter
        fields = ["person", "postmark_date", "issue", "notes"]
        widgets = {"notes": note_field}

    person = make_ajax_field(Letter, "person", "person_contrib_channel")
    issue = forms.ChoiceField(
        choices=[("", "-----"), *LetterIssue.IssueTypes.choices], required=False
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_notes(self):
        self.notes = self.cleaned_data.get("notes")
        return ""

    def save(self, commit=True):
        letter = super().save()
        letter.created_by = self.user
        letter.save()
        if issue := self.cleaned_data.get("issue"):
            issue = LetterIssue.objects.create(
                letter=letter,
                issue=issue,
                additional_note=self.notes,
                created_by=self.user,
                created_date=datetime.now(),
            )
            issue.save()


class ContribPersonForm(PersonAdminForm):
    class Meta(PersonAdminForm.Meta):
        model = Person
        fields = [
            "inmate_number",
            "last_name",
            "first_name",
            "middle_name",
            "name_suffix",
            "prison",
            "issue",
            "notes",
        ]
        required_fields = ["inmate_number", "last_name", "first_name", "prison"]
        widgets = {
            "notes": note_field,
            "middle_name": forms.TextInput(
                attrs={
                    "placeholder": "Optional",
                },
            ),
            "name_suffix": forms.TextInput(
                attrs={
                    "placeholder": "Optional",
                },
            ),
        }

    prison = forms.ModelChoiceField(queryset=Prison.objects.all().order_by("name"))
    issue = forms.ChoiceField(
        choices=[("", "-----"), *PersonIssue.IssueTypes.choices], required=False
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_notes(self):
        self.notes = self.cleaned_data.get("notes")
        return ""

    def save(self, commit=True):
        person = super().save()
        person.created_by = self.user
        person.save()
        data = self.cleaned_data
        person_prison = PersonPrison(
            person=person, prison=data["prison"], created_date=datetime.now(), created_by=self.user
        )
        person_prison.save()
        if issue := self.cleaned_data.get("issue"):
            issue = PersonIssue.objects.create(
                person=person,
                issue=issue,
                additional_note=self.notes,
                created_by=self.user,
                created_date=datetime.now(),
            )
            issue.save()


class ContribIssueForm(ModelForm):
    issue_type = ""

    class Meta:
        abstract = True
        fields = ["issue", "additional_note"]
        required_fields = ["issue"]
        widgets = {
            "additional_note": forms.Textarea(
                attrs={
                    "rows": 3,
                    "cols": 40,
                    "placeholder": "Only fill this out if there is a problem that needs review by PPBP staff.",
                },
            ),
        }

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_issue_type(self):
        if issue_target := self.cleaned_data.get(self.issue_type):
            if not issue_target.created_by == self.user:
                raise ValidationError(
                    f"User is not the creator of this {self.issue_type}, cannot add note."
                )
        return issue_target

    def save(self, commit=True):
        issue = super().save()
        issue.created_by = self.user
        issue.save()


class ContribPersonIssueForm(ContribIssueForm):
    issue_type = "person"

    class Meta(ContribIssueForm.Meta):
        model = PersonIssue
        fields = [*ContribIssueForm.Meta.fields, "person"]
        widgets = ContribIssueForm.Meta.widgets | {"person": forms.HiddenInput()}

    def clean_person(self):
        return self.clean_issue_type()


class ContribLetterIssueForm(ContribIssueForm):
    issue_type = "letter"

    class Meta(ContribIssueForm.Meta):
        model = LetterIssue
        fields = [*ContribIssueForm.Meta.fields, "letter"]
        widgets = ContribIssueForm.Meta.widgets | {"letter": forms.HiddenInput()}

    def clean_letter(self):
        return self.clean_issue_type()


class RegistrationForm(DjRegistrationForm):
    class Meta(DjRegistrationForm.Meta):
        fields = DjRegistrationForm.Meta.fields + ["first_name", "last_name"]

    def clean(self):
        self.cleaned_data["email"] = self.cleaned_data["email"].lower()
        return super().clean()


class AuthenticationForm(DjAuthenticationForm):
    @sensitive_variables()
    def clean(self):
        self.cleaned_data["username"] = self.cleaned_data.get("username", "").lower()
        return super().clean()


class PasswordResetForm(DjPasswordResetForm):
    @sensitive_variables()
    def clean(self):
        self.cleaned_data["username"] = self.cleaned_data.get("username", "").lower()
        return super().clean()
