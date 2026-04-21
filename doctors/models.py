from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse


class Specialty(models.Model):
    name = models.CharField('название', max_length=100, unique=True)
    description = models.TextField('описание', blank=True)
    icon = models.ImageField(
        'иконка', upload_to='specialties/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'svg', 'webp'])],
    )

    class Meta:
        verbose_name = 'специализация'
        verbose_name_plural = 'специализации'
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(
        'users.User', on_delete=models.CASCADE,
        related_name='doctor_profile', verbose_name='пользователь'
    )
    specialties = models.ManyToManyField(
        Specialty, through='DoctorSpecialty',
        related_name='doctors', verbose_name='специализации', blank=True
    )
    experience_years = models.PositiveIntegerField('стаж (лет)', default=0)
    education = models.TextField('образование', blank=True)
    bio = models.TextField('о враче', blank=True)
    photo = models.ImageField(
        'фото', upload_to='doctors/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )
    photo_url = models.URLField('ссылка на фото', blank=True)
    consultation_price = models.DecimalField(
        'цена консультации', max_digits=10, decimal_places=2, default=0
    )
    is_available = models.BooleanField('доступен', default=True)

    class Meta:
        verbose_name = 'врач'
        verbose_name_plural = 'врачи'
        ordering = ['-experience_years']

    def __str__(self):
        full_name = self.user.get_full_name().strip()
        return full_name or self.user.email

    def get_absolute_url(self):
        return reverse('doctor-detail', kwargs={'pk': self.pk})

    def get_rating(self):
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg('rating'))
        return result['avg'] or 0


class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='врач')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name='специализация')
    is_primary = models.BooleanField('основная', default=False)

    class Meta:
        verbose_name = 'специализация врача'
        verbose_name_plural = 'специализации врачей'
        unique_together = ('doctor', 'specialty')

    def __str__(self):
        return str(self.specialty)


class Schedule(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Понедельник'
        TUESDAY = 1, 'Вторник'
        WEDNESDAY = 2, 'Среда'
        THURSDAY = 3, 'Четверг'
        FRIDAY = 4, 'Пятница'
        SATURDAY = 5, 'Суббота'
        SUNDAY = 6, 'Воскресенье'

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE,
        related_name='schedules', verbose_name='врач'
    )
    day_of_week = models.IntegerField('день недели', choices=DayOfWeek.choices)
    start_time = models.TimeField('начало')
    end_time = models.TimeField('конец')

    class Meta:
        verbose_name = 'расписание'
        verbose_name_plural = 'расписания'
        unique_together = ('doctor', 'day_of_week')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return self.get_day_of_week_display()
