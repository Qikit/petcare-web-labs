from django.db import models
from django.urls import reverse


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        CONFIRMED = 'confirmed', 'Подтверждена'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    client = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='клиент'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='врач'
    )
    pet = models.ForeignKey(
        'pets.Pet', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='питомец'
    )
    service = models.ForeignKey(
        'services.Service', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='услуга'
    )
    date = models.DateField('дата приёма')
    time_slot = models.TimeField('время')
    status = models.CharField(
        'статус', max_length=20,
        choices=Status.choices, default=Status.PENDING
    )
    comment = models.TextField('комментарий', blank=True)
    cancel_reason = models.TextField('причина отмены', blank=True)
    created_at = models.DateTimeField('создана', auto_now_add=True)
    updated_at = models.DateTimeField('обновлена', auto_now=True)

    class Meta:
        verbose_name = 'запись на приём'
        verbose_name_plural = 'записи на приём'
        ordering = ['-date', '-time_slot']

    def __str__(self):
        return f'Запись #{self.pk} — {self.client} к {self.doctor} ({self.date})'

    def get_absolute_url(self):
        return reverse('appointment-list')

    def can_cancel(self):
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)

    def is_upcoming(self):
        from datetime import datetime
        from django.utils import timezone
        appointment_dt = datetime.combine(self.date, self.time_slot)
        return appointment_dt > timezone.now().replace(tzinfo=None) and self.status != self.Status.CANCELLED

    def save(self, *args, **kwargs):
        if not self.pk and not self.status:
            self.status = self.Status.PENDING
        super().save(*args, **kwargs)


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE,
        related_name='medical_record', verbose_name='запись на приём'
    )
    pet = models.ForeignKey(
        'pets.Pet', on_delete=models.CASCADE,
        related_name='medical_records', verbose_name='питомец'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.CASCADE,
        related_name='medical_records', verbose_name='врач'
    )
    diagnosis = models.TextField('диагноз')
    treatment = models.TextField('лечение', blank=True)
    recommendations = models.TextField('рекомендации', blank=True)
    attachment = models.FileField(
        'файл (анализы)', upload_to='medical_records/',
        blank=True, null=True
    )
    created_at = models.DateTimeField('создана', auto_now_add=True)

    class Meta:
        verbose_name = 'медицинская карта'
        verbose_name_plural = 'медицинские карты'
        ordering = ['-created_at']

    def __str__(self):
        diag = self.diagnosis[:50] if self.diagnosis else ''
        return f'Карта #{self.pk} — {self.pet.name} ({diag})'
