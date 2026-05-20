from datetime import datetime
from ajax_select import make_ajax_field
from django import forms
from django.forms import ModelForm, ValidationError

from src.app.models.letter import Letter
from src.app.models.person import Person

from src.app.models.prison import PersonPrison, Prison

from src.app.admin.person import PersonAdminForm

from src.app.admin.letter import LetterForm


class ContribLetterForm(LetterForm):

    person = make_ajax_field(Letter, "person", "person_contrib_channel")

    class Meta(LetterForm.Meta):
        model = Letter
        fields = ["person", "postmark_date", "notes"]

    def save(self, user): # type: ignore
        letter = super().save()
        letter.created_by = user
        letter.save()


class ContribPersonForm(PersonAdminForm):

    prison = forms.ModelChoiceField(queryset=Prison.objects.all().order_by("name"))

    class Meta(PersonAdminForm.Meta):
        model = Person
        fields = ["inmate_number", "last_name", "first_name", "middle_name", "name_suffix", "prison", "notes"]
        required_fields = ["inmate_number", "last_name", "first_name", "prison"]

    def save(self, user):  # type: ignore
        saved_person = super().save()
        saved_person.created_by = user
        saved_person.save()
        data = self.cleaned_data
        person_prison = PersonPrison(person=saved_person, prison=data["prison"], created_date=datetime.now(), created_by=user)
        person_prison.save()
