from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from doctors.models import Doctor, Schedule
from doctors.scheduling import get_available_slots


User = get_user_model()


class AvailableSlotsTest(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(
            email='doc@test.ru', password='pass1234', role='veterinarian',
            first_name='Тест', last_name='Доктор',
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, experience_years=5,
            consultation_price=Decimal('1000'),
        )
        for day in range(7):
            Schedule.objects.create(
                doctor=self.doctor, day_of_week=day,
                start_time=time(9, 0), end_time=time(12, 0),
            )

    def test_returns_slots(self):
        slots = get_available_slots(self.doctor, days_ahead=2)
        self.assertGreater(len(slots), 0)

    def test_excludes_busy_slot(self):
        from appointments.models import Appointment
        from pets.models import Pet
        from services.models import Service

        client_user = User.objects.create_user(email='c@t.ru', password='p')
        pet = Pet.objects.create(owner=client_user, name='P', species='cat', age=24)
        svc = Service.objects.create(
            name='S', price=Decimal('100'), duration_minutes=30,
        )
        tomorrow = timezone.localtime().date() + timedelta(days=1)
        Appointment.objects.create(
            client=client_user, doctor=self.doctor, pet=pet, service=svc,
            date=tomorrow, time_slot=time(9, 0), status='confirmed',
        )
        slots = get_available_slots(self.doctor, days_ahead=2)
        match = [s for s in slots if s['date'] == tomorrow and s['time'] == time(9, 0)]
        self.assertEqual(match, [])
