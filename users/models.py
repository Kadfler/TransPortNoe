from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('admin', 'Администратор'),
        ('dispatcher', 'Логист'),
        ('driver', 'Водитель'),
    )

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=16, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class DriverProfile(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50)
    STATUS_CHOICES = (
        ('free', 'Свободен'),
        ('busy', 'В рейсе'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"