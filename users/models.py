from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Клиент'
        VETERINARIAN = 'veterinarian', 'Ветеринар'
        ADMIN = 'admin', 'Администратор'

    username = None
    email = models.EmailField('электронная почта', unique=True)
    phone = models.CharField('телефон', max_length=20, blank=True)
    role = models.CharField('роль', max_length=20, choices=Role.choices, default=Role.CLIENT)
    avatar = models.ImageField('аватар', upload_to='avatars/', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        name = f'{self.first_name} {self.last_name}'.strip()
        return name if name else self.email

    def get_absolute_url(self):
        return reverse('profile')
