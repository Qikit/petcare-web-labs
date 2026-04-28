from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Doctor, Specialty
from services.models import Service


User = get_user_model()


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


class SearchViewTest(TestCase):
    def setUp(self):
        self.spec = Specialty.objects.create(name='Терапия', description='общий приём')
        user = User.objects.create_user(
            email='vet@test.ru', password='p', first_name='Иван', last_name='Терапевтов',
            role='veterinarian',
        )
        self.doctor = Doctor.objects.create(
            user=user, experience_years=5, consultation_price=Decimal('1000'),
            bio='лечит по терапии',
        )
        Service.objects.create(
            name='Терапевтический приём',
            description='первичный',
            price=Decimal('500'),
            duration_minutes=20,
            specialty=self.spec,
        )

    def test_empty_query_renders_form(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Поиск')
        self.assertNotContains(response, 'Ничего не найдено')

    def test_query_finds_results(self):
        response = self.client.get(reverse('search'), {'q': 'Терап'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Терапия')
        self.assertContains(response, 'Терапевтический приём')

    def test_query_no_match(self):
        response = self.client.get(reverse('search'), {'q': 'xxxnomatchxxx'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ничего не найдено')


class IndexWidgetsTest(TestCase):
    def test_index_renders_with_widgets(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Топ врачей')
        self.assertContains(response, 'Популярные услуги')
        self.assertContains(response, 'Направления')
        self.assertContains(response, 'Свежие отзывы')
