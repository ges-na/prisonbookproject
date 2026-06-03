from datetime import datetime

from ajax_select import make_ajax_field
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django_registration.forms import RegistrationForm as DjRegistrationForm

from src.app.admin.letter import LetterForm
from src.app.admin.person import PersonAdminForm
from src.app.models.letter import Letter
from src.app.models.person import Person
from src.app.models.prison import PersonPrison, Prison
from src.app.models.problem_note import ProblemNote
from src.auth.models import User


class ContribLetterForm(LetterForm):
    person = make_ajax_field(Letter, "person", "person_contrib_channel")

    class Meta(LetterForm.Meta):
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

    def __init__(self, user: User):
        super().__init__()
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
        super().clean()
        self.cleaned_data["email"] = self.cleaned_data["email"].lower()
