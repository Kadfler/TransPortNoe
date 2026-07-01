from django.db import models
from users.models import CustomUser

class Vehicle(models.Model):
    TYPE_CHOICES = (
        ('tent', 'Тент'),
        ('ref', 'Рефрижератор'),
    )
    mark = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=20)
    body_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    capacity = models.FloatField(help_text="Грузоподъемность в тоннах")
    base_rate_per_km = models.DecimalField(max_digits=10, decimal_places=2)

    driver = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'driver'},
        verbose_name="Водитель"
    )

    mileage = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Транспорт"
        verbose_name_plural = "Транспорт"