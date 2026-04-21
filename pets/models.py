from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Pet(models.Model):
    class Species(models.TextChoices):
        CAT = 'cat', 'Кошка'
        DOG = 'dog', 'Собака'
        BIRD = 'bird', 'Птица'
        RODENT = 'rodent', 'Грызун'
        REPTILE = 'reptile', 'Рептилия'
        OTHER = 'other', 'Другое'

    owner = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='pets', verbose_name='владелец'
    )
    name = models.CharField('кличка', max_length=100)
    species = models.CharField('вид', max_length=20, choices=Species.choices)
    breed = models.CharField('порода', max_length=100, blank=True)
    age = models.PositiveIntegerField(
        'возраст (мес.)', validators=[MaxValueValidator(360)]
    )
    weight = models.DecimalField(
        'вес (кг)', max_digits=6, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0.01), MaxValueValidator(999.99)]
    )
    health_notes = models.TextField('заметки о здоровье', blank=True)
    photo = models.ImageField(
        'фото', upload_to='pets/', blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )
    created_at = models.DateTimeField('добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'питомец'
        verbose_name_plural = 'питомцы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_species_display()})'

    def get_absolute_url(self):
        return reverse('pet-list')
