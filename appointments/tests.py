from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from users.models import User
from doctors.models import Doctor, Specialty
from pets.models import Pet
from services.models import Service
from appointments.models import Appointment, MedicalRecord


class MedicalRecordPdfAuthzTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.ru', password='pwd12345',
            first_name='Owner', last_name='Test',
        )
        self.stranger = User.objects.create_user(
            email='stranger@test.ru', password='pwd12345',
            first_name='Stranger', last_name='Test',
        )
        vet_user = User.objects.create_user(
            email='vet@test.ru', password='pwd12345',
            first_name='Vet', last_name='Test',
            role=User.Role.VETERINARIAN,
        )
        specialty = Specialty.objects.create(name='Терапия')
        self.doctor = Doctor.objects.create(user=vet_user, consultation_price=Decimal('1000'))
        self.doctor.specialties.add(specialty)
        self.pet = Pet.objects.create(owner=self.owner, name='Барсик', species='cat', age=24)
        self.service = Service.objects.create(name='Осмотр', price=Decimal('1000'), duration_minutes=30)
        self.appointment = Appointment.objects.create(
            client=self.owner, doctor=self.doctor, pet=self.pet, service=self.service,
            date=date.today() - timedelta(days=1), time_slot=time(10, 0),
            status=Appointment.Status.COMPLETED,
        )
        self.record = MedicalRecord.objects.create(
            appointment=self.appointment, pet=self.pet, doctor=self.doctor,
            diagnosis='test', treatment='test',
        )

    def test_owner_can_download_pdf(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('medical-record-pdf', args=[self.record.pk]))
        self.assertEqual(response.status_code, 200)

    def test_stranger_cannot_download_pdf(self):
        self.client.force_login(self.stranger)
        response = self.client.get(reverse('medical-record-pdf', args=[self.record.pk]))
        self.assertEqual(response.status_code, 404)
