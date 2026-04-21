from django.core.validators import FileExtensionValidator
from django.db import models


class Service(models.Model):
    name = models.CharField('название', max_length=200)
    description = models.TextField('описание', blank=True)
    price = models.DecimalField('цена', max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField('длительность (мин.)', default=30)
    specialty = models.ForeignKey(
        'doctors.Specialty', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='services', verbose_name='специализация'
    )
    photo = models.ImageField(
        'фото', upload_to='services/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )
    is_active = models.BooleanField('активна', default=True)

    class Meta:
        verbose_name = 'услуга'
        verbose_name_plural = 'услуги'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — {self.price} руб.'
