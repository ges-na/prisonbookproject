from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

from src.app.models.person import Person
from src.app.models.prison import PersonPrison
from src.auth.models import User


class TestAdminEndpoints(TestCase):
    prison_formset = {
        "prisons-TOTAL_FORMS": 1,
        "prisons-INITIAL_FORMS": 0,
        "prisons-MIN_NUM_FORMS": 0,
        "prisons-MAX_NUM_FORMS": 1,
    }
    personissue_formset = {
        "personissue_set-TOTAL_FORMS": 0,
        "personissue_set-INITIAL_FORMS": 0,
        "personissue_set-MIN_NUM_FORMS": 0,
        "personissue_set-MAX_NUM_FORMS": 1000,
    }
    letterissue_formset = {
        "letterissue_set-TOTAL_FORMS": 0,
        "letterissue_set-INITIAL_FORMS": 0,
        "letterissue_set-MIN_NUM_FORMS": 0,
        "letterissue_set-MAX_NUM_FORMS": 1000,
    }

    def setUp(self):
        self.credentials = {"email": "a@b.com", "password": "pass"}
        self.user = User.objects.create(**self.credentials, is_staff=True, is_superuser=True)
        self.client = Client()
        self.client.force_login(self.user)
        self.person = baker.make("app.Person")
        self.prison = baker.make("app.Prison")
        self.personprison = PersonPrison.objects.create(person=self.person, prison=self.prison)
        self.letter = baker.make("app.Letter", person=self.person)
        self.letterissue = baker.make("app.LetterIssue", letter=self.letter)
        self.personissue = baker.make("app.PersonIssue", person=self.person)

    # def test_login(self):
    #     response = self.client.post(reverse("django_login"), **self.credentials)
    #     self.assertEqual(response.status_code, 200)

    def test_person_changelist(self):
        response = self.client.get(reverse("admin:app_person_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_letter_changelist(self):
        response = self.client.get(reverse("admin:app_letter_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_prison_changelist(self):
        response = self.client.get(reverse("admin:app_prison_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_person_issue_changelist(self):
        response = self.client.get(reverse("admin:app_personissue_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_letter_issue_changelist(self):
        response = self.client.get(reverse("admin:app_letterissue_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_user_changelist(self):
        response = self.client.get(reverse("admin:CustomAuth_user_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_person_add(self):
        response = self.client.post(
            reverse("admin:app_person_add"),
            {
                "inmate_number": "JK3495",
                "last_name": "test_lname2",
                "first_name": "test_fname2",
                "prisons-0-prison": self.prison.id,
            }
            | self.personissue_formset
            | self.prison_formset,
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
            | self.personissue_formset
            | self.prison_formset,
        )
        self.assertEqual(response.status_code, 302)
        person = Person.objects.get(inmate_number="JK3495")
        assert person
        response = self.client.post(
            reverse("admin:app_person_change", args={"person": person.id}),
            {
                "inmate_number": "JK3494",
                "last_name": "test_lname2",
                "first_name": "test_fname2",
                "prisons-0-prison": self.prison.id,
            }
            | self.personissue_formset
            | self.prison_formset,
        )
        self.assertEqual(response.status_code, 302)
        assert Person.objects.get(inmate_number="JK3494")
        assert not Person.objects.get(inmate_number="JK3495")
