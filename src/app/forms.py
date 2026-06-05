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
from src.app.models.letter import Letter
from src.app.models.person import Person
from src.app.models.prison import PersonPrison, Prison
from src.app.models.problem_note import ProblemNote
from src.auth.models import User

# TODO: split into different files


class ContribLetterForm(LetterAdminForm):
    person = make_ajax_field(Letter, "person", "person_contrib_channel")

    class Meta(LetterAdminForm.Meta):
        model = Letter
        fields = ["person", "postmark_date", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "cols": 40,
                    "placeholder": "Only fill this out if there is a problem that needs review by PPBP staff.",
                },
            ),
        }

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def save(self, commit=True):
        letter = super().save()
        letter.created_by = self.user
        letter.save()
        if note := self.cleaned_data.get("notes"):
            problem_note = ProblemNote(letter=letter, note=note, created_by=self.user)
            problem_note.save()


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
            "notes",
        ]
        required_fields = ["inmate_number", "last_name", "first_name", "prison"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "cols": 40,
                    "placeholder": "Only fill this out if there is a problem that needs review by PPBP staff.",
                },
            ),
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

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def save(self, commit=True):
        person = super().save()
        person.created_by = self.user
        person.save()
        data = self.cleaned_data
        person_prison = PersonPrison(
            person=person, prison=data["prison"], created_date=datetime.now(), created_by=self.user
        )
        person_prison.save()
        if note := self.cleaned_data.get("notes"):
            problem_note = ProblemNote(person=person, note=note, created_by=self.user)
            problem_note.save()


class ContribProblemNoteForm(ModelForm):
    class Meta:
        model = ProblemNote
        fields = ["note", "letter", "person"]
        required_fields = ["note"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "cols": 40,
                    "placeholder": "Only fill this out if there is a problem that needs review by PPBP staff.",
                },
            ),
            "letter": forms.HiddenInput(),
            "person": forms.HiddenInput(),
        }

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        for note_type in ["letter", "person"]:
            if note_value := self.cleaned_data.get(note_type):
                if not note_value.created_by == self.user:
                    raise ValidationError(
                        f"User is not the creator of this {note_type}, cannot add note."
                    )
        note = super().save()
        note.created_by = self.user
        note.save()


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
