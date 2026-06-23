from datetime import UTC, datetime, timedelta

from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

from app.utils import WorkflowStage
from src.app.models.person import ELIGIBILITY_INTERVAL_DAYS, Person
from src.app.models.prison import PersonPrison
from src.auth.models import User
from src.tests.utils import personissue_formset, prison_formset

"""
TODO:
- separate admin and model tests
- test admin form fields, filters, form clean methods
- test model save, created/modified
"""


class TestPerson(TestCase):
    def setUp(self):
        self.credentials = {"email": "a@b.com", "password": "pass"}
        self.user = User.objects.create(**self.credentials, is_staff=True, is_superuser=True)
        self.client = Client()
        self.client.force_login(self.user)
        self.person = baker.make("app.Person")
        self.no_relations_person = baker.make("app.Person")
        self.prison = baker.make("app.Prison")
        self.personprison = PersonPrison.objects.create(person=self.person, prison=self.prison)
        self.letter = baker.make("app.Letter", person=self.person)
        self.personissue = baker.make("app.PersonIssue", person=self.person)

    def test_person_add(self):
        response = self.client.post(
            reverse("admin:app_person_add"),
            {
                "inmate_number": "JK3495",
                "last_name": "test_lname2",
                "first_name": "test_fname2",
                "prisons-0-prison": self.prison.id,
            }
            | personissue_formset
            | prison_formset,
        )
        self.assertEqual(response.status_code, 302)
        assert Person.objects.get(inmate_number="JK3495")

    def test_person_change(self):
        response = self.client.post(
            reverse("admin:app_person_add"),
            {
                "inmate_number": "JK3495",
                "last_name": "test_lname2",
                "first_name": "test_fname2",
                "prisons-0-prison": self.prison.id,
            }
            | personissue_formset
            | prison_formset,
        )
        self.assertEqual(response.status_code, 302)
        person = Person.objects.filter(inmate_number="JK3495").first()
        assert person
        response = self.client.post(
            reverse("admin:app_person_change", args=(person.id,)),
            {
                "inmate_number": "JK3494",
                "last_name": "test_lname2",
                "first_name": "test_fname2",
                "prisons-0-prison": self.prison.id,
                "_save": "Save",
            }
            | personissue_formset
            | prison_formset,
        )
        self.assertEqual(response.status_code, 302)
        assert Person.objects.filter(inmate_number="JK3494").first()
        assert not Person.objects.filter(inmate_number="JK3495")

    def test_property_current_prison(self):
        assert self.person.current_prison == self.prison
        assert not self.no_relations_person.current_prison
        PersonPrison.objects.create(person=self.no_relations_person, prison=self.prison)
        assert self.no_relations_person.current_prison == self.prison

    def test_property_last_served(self):
        assert not self.person.last_served
        date = datetime.now(tz=UTC)
        baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.FULFILLED,
            fulfilled_date=date,
        )
        assert self.person.last_served == date

    def test_property_has_been_served(self):
        assert not self.person.has_been_served
        baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.FULFILLED,
            fulfilled_date=datetime.now(tz=UTC),
        )
        assert self.person.has_been_served

    def test_property_pending_letters(self):
        assert self.person.pending_letters.first() == self.letter
        self.letter.workflow_stage = WorkflowStage.FULFILLED
        self.letter.save()
        assert not self.person.pending_letters

    def test_property_pending_letter_count(self):
        assert self.person.pending_letter_count == 1
        self.letter.workflow_stage = WorkflowStage.FULFILLED
        self.letter.save()
        assert self.person.pending_letter_count == 0

    def test_property_has_pending_letters(self):
        assert self.person.has_pending_letters == True
        self.letter.workflow_stage = WorkflowStage.FULFILLED
        self.letter.save()
        assert not self.person.has_pending_letters

    def test_property_package_count(self):
        assert self.person.package_count == 0
        self.letter.workflow_stage = WorkflowStage.FULFILLED
        self.letter.save()
        assert self.person.package_count == 1
        assert self.no_relations_person.package_count == 0

    def test_property_all_letters(self):
        assert self.person.all_letters.count() == 1
        assert self.person.all_letters.first() == self.letter
        baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.FULFILLED,
            fulfilled_date=datetime.now(tz=UTC),
        )
        assert self.person.all_letters.count() == 2
        assert self.no_relations_person.all_letters.count() == 0

    def test_property_letter_count(self):
        assert self.person.letter_count == 1
        baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.FULFILLED,
            fulfilled_date=datetime.now(tz=UTC),
        )
        assert self.person.letter_count == 2
        assert self.no_relations_person.letter_count == 0

    def test_property_name_str(self):
        # TODO should capitalization take place in model clean?
        new_person = Person.objects.create(
            inmate_number="test",
            first_name="fname",
            last_name="lname",
            middle_name="middle",
            name_suffix="jr.",
        )
        assert new_person.name_str == "fname middle lname jr."

    def test_property_eligible(self):
        # never served, default eligibile
        assert not self.person.last_served
        assert self.person.eligible
        # served today, not eligible
        new_letter = baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.FULFILLED,
            fulfilled_date=datetime.now(),
        )
        assert not self.person.eligible
        # last served ELIGIBILITY_INTERVAL_DAYS ago, eligible
        new_letter.fulfilled_date = datetime.now() - timedelta(days=ELIGIBILITY_INTERVAL_DAYS)
        new_letter.save()
        assert self.person.eligible

    def test_property_open_issues(self):
        assert self.person.open_issues
        self.personissue.resolved = True
        self.personissue.save()
        assert not self.person.open_issues

    def test_person_get_eligibility_str(self):
        # eligible, one letter pending
        assert self.person.has_pending_letters and self.person.eligible
        # not eligible, no letters pending
        assert self.person.get_eligibility_str(links=False) == "Eligible; 1 letters pending"
        self.letter.workflow_stage = WorkflowStage.FULFILLED
        self.letter.fulfilled_date = datetime.now()
        self.letter.save()
        assert not self.person.eligible
        eligible_dt = (datetime.now() + timedelta(days=ELIGIBILITY_INTERVAL_DAYS)).strftime(
            "%B %-d, %Y"
        )
        assert self.person.get_eligibility_str(links=False) == f"Eligible after {eligible_dt}"
        # not eligible, one letter pending
        baker.make(
            "app.Letter",
            person=self.person,
            workflow_stage=WorkflowStage.STAGE1_COMPLETE,
        )
        assert self.person.has_pending_letters and not self.person.eligible
        assert (
            self.person.get_eligibility_str(links=False)
            == f"Eligible after {eligible_dt}; 1 letters pending"
        )
        # eliginle, no letters pending
        assert self.no_relations_person.get_eligibility_str() == "Eligible"
