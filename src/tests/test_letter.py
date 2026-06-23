from django.test import Client, TestCase
from model_bakery import baker

from src.app.models.prison import PersonPrison
from src.auth.models import User


class TestLetter(TestCase):
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
        self.letterissue = baker.make("app.LetterIssue", letter=self.letter)

    def test_property_open_issues(self):
        pass

    def test_str(self):
        pass

    def test_created_by(self):
        pass

    def test_created_date(self):
        pass

    def test_modified_date(self):
        pass

    #########
    # Admin #
    #########

    def test_admin_form_clean(self):
        pass

    def test_letter_name(self):
        pass

    def test_person_list_display(self):
        pass

    def test_restrictions(self):
        pass

    def test_prison_mailing_address(self):
        pass
