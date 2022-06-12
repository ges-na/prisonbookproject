import os

from django.test import TestCase
from django.contrib.auth.models import User

from model_bakery import baker


class ImportTests(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin')
        self.admin_user.set_password('Password123')
        self.admin_user.save()
        self.client.login(username='admin', password='Password123')

    def test_import_file(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'test_test_db.csv')
        with open(filename, "rb") as f:
            data = {
                    'input_format': 0,
                    'import_file': f
            }
            self.response = self.client.post('/admin/app/person/import/', data)
        self.assertIn('confirm_form', self.response.context)
        data = self.response.context['confirm_form'].initial
        self.confirm_response = self.client.post('/admin/app/person/process_import/', data, follow=True)
        self.assertContains(self.response, '123')

class ExportTests(TestCase):

    def setUp(self):
        self.person = baker.make('app.Person')
        self.admin_user = User.objects.create_superuser(username='admin')
        self.admin_user.set_password('Password123')
        self.admin_user.save()
        self.client.login(username='admin', password='Password123')

    def test_admin_login(self):
        self.response = self.client.get('/admin/')
        self.assertEqual(self.response.status_code, 200)

    def test_export_file(self):
        self.response = self.client.post('/admin/app/person/export/', {'file_format': '0'})
        self.assertContains(self.response, self.person.last_name)

    def test_export_file_false(self):
        self.response = self.client.post('/admin/app/person/export/', {'file_format': '0'})
        self.assertNotContains(self.response, 'randomstring')
