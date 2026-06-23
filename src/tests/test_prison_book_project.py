from django.test import Client, TestCase
from django.urls import reverse

from src.auth.models import User


class TestAdminEndpoints(TestCase):
    def setUp(self):
        self.credentials = {"email": "a@b.com", "password": "pass"}
        self.user = User.objects.create(**self.credentials, is_staff=True, is_superuser=True)
        self.client = Client()
        self.client.force_login(self.user)

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
