from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Specialty
from services.models import Service


User = get_user_model()


class ServiceCrudTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff@test.ru', password='pass1234',
            is_staff=True,
        )
        self.regular = User.objects.create_user(
            email='user@test.ru', password='pass1234',
        )
        self.spec = Specialty.objects.create(name='ТестСпец')
        self.service = Service.objects.create(
            name='Тестовая услуга',
            description='Описание',
            price=Decimal('1000'),
            duration_minutes=30,
            specialty=self.spec,
        )

    def test_detail_accessible_for_anyone(self):
        response = self.client.get(reverse('service-detail', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая услуга')

    def test_create_redirects_anon(self):
        response = self.client.get(reverse('service-create'))
        self.assertEqual(response.status_code, 302)

    def test_create_redirects_non_staff(self):
        self.client.login(email='user@test.ru', password='pass1234')
        response = self.client.get(reverse('service-create'))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_create(self):
        self.client.login(email='staff@test.ru', password='pass1234')
        response = self.client.post(reverse('service-create'), {
            'name': 'Новая услуга',
            'description': 'desc',
            'price': '500',
            'duration_minutes': '20',
            'specialty': self.spec.pk,
            'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Service.objects.filter(name='Новая услуга').exists())

    def test_staff_can_edit(self):
        self.client.login(email='staff@test.ru', password='pass1234')
        response = self.client.post(
            reverse('service-edit', args=[self.service.pk]),
            {
                'name': 'Изменённая',
                'description': 'desc',
                'price': '1500',
                'duration_minutes': '30',
                'specialty': self.spec.pk,
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.service.refresh_from_db()
        self.assertEqual(self.service.name, 'Изменённая')

    def test_staff_can_delete(self):
        self.client.login(email='staff@test.ru', password='pass1234')
        pk = self.service.pk
        response = self.client.post(reverse('service-delete', args=[pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Service.objects.filter(pk=pk).exists())

    def test_non_staff_cannot_delete(self):
        self.client.login(email='user@test.ru', password='pass1234')
        pk = self.service.pk
        response = self.client.post(reverse('service-delete', args=[pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Service.objects.filter(pk=pk).exists())
