from django import forms
from django.utils import timezone

from doctors.models import Schedule
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'pet', 'service', 'date', 'time_slot', 'comment')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарий (необязательно)'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'pet': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['pet'].queryset = user.pets.all()

    def clean_date(self):
        date_value = self.cleaned_data['date']
        if date_value < timezone.now().date():
            raise forms.ValidationError('Нельзя записаться на прошедшую дату')
        return date_value

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        date_value = cleaned.get('date')
        time_slot = cleaned.get('time_slot')
        if not (doctor and date_value and time_slot):
            return cleaned

        schedule = Schedule.objects.filter(
            doctor=doctor, day_of_week=date_value.weekday(),
        ).first()
        if schedule is None:
            raise forms.ValidationError('Врач не работает в выбранный день недели')
        if not (schedule.start_time <= time_slot < schedule.end_time):
            raise forms.ValidationError(
                f'Врач работает с {schedule.start_time:%H:%M} до {schedule.end_time:%H:%M}',
            )

        conflict = Appointment.objects.filter(
            doctor=doctor, date=date_value, time_slot=time_slot,
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
                Appointment.Status.IN_PROGRESS,
            ],
        )
        if self.instance.pk:
            conflict = conflict.exclude(pk=self.instance.pk)
        if conflict.exists():
            raise forms.ValidationError('Этот слот уже занят, выберите другое время')

        return cleaned
