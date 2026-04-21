from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import User
from doctors.models import Doctor, Specialty
from pets.models import Pet
from services.models import Service
from appointments.models import Appointment
from reviews.models import Review


class ReviewAuthzTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@test.ru', password='pwd12345',
        )
        self.stranger = User.objects.create_user(
            email='stranger@test.ru', password='pwd12345',
        )
        vet_user = User.objects.create_user(
            email='vet@test.ru', password='pwd12345',
            role=User.Role.VETERINARIAN,
        )
        self.doctor = Doctor.objects.create(user=vet_user, consultation_price=Decimal('1000'))
        self.doctor.specialties.add(Specialty.objects.create(name='Терапия'))
        self.pet = Pet.objects.create(owner=self.client_user, name='Барсик', species='cat', age=24)
        self.service = Service.objects.create(name='Осмотр', price=Decimal('1000'), duration_minutes=30)
        self.completed_apt = Appointment.objects.create(
            client=self.client_user, doctor=self.doctor, pet=self.pet, service=self.service,
            date=date.today() - timedelta(days=1), time_slot=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )
        self.pending_apt = Appointment.objects.create(
            client=self.client_user, doctor=self.doctor, pet=self.pet, service=self.service,
            date=date.today() + timedelta(days=1), time_slot=time(11, 0),
            status=Appointment.Status.PENDING,
        )

    def _post(self, apt_pk, rating=5, text='Отлично'):
        return self.client.post(
            reverse('review-create', args=[apt_pk]),
            {'rating': rating, 'text': text},
        )

    def test_client_can_review_completed_appointment(self):
        self.client.force_login(self.client_user)
        response = self._post(self.completed_apt.pk)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(appointment=self.completed_apt).exists())

    def test_client_cannot_review_pending_appointment(self):
        self.client.force_login(self.client_user)
        response = self._post(self.pending_apt.pk)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Review.objects.filter(appointment=self.pending_apt).exists())

    def test_stranger_cannot_review_other_clients_appointment(self):
        self.client.force_login(self.stranger)
        response = self._post(self.completed_apt.pk)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Review.objects.exists())

    def test_duplicate_review_rejected(self):
        self.client.force_login(self.client_user)
        self._post(self.completed_apt.pk)
        response = self._post(self.completed_apt.pk)
        self.assertEqual(Review.objects.filter(appointment=self.completed_apt).count(), 1)
        self.assertEqual(response.status_code, 302)
