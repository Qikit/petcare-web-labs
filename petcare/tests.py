from django.test import TestCase
from django.urls import reverse


class PublicPagesSmokeTest(TestCase):
    def test_index_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_list_200(self):
        response = self.client.get(reverse('doctor-list'))
        self.assertEqual(response.status_code, 200)

    def test_service_list_200(self):
        response = self.client.get(reverse('service-list'))
        self.assertEqual(response.status_code, 200)

    def test_login_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
