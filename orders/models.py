from django.db import models
from users.models import CustomUser, DriverProfile
from vehicles.models import Vehicle
from routes.models import Route
from geopy.geocoders import Nominatim
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    tax_profile = models.CharField(max_length=50, help_text="НДС / без НДС")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('in_progress', 'В пути'),
        ('completed', 'Завершен'),
    )
    client = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    description = models.TextField(default='', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")

    # Текстовые поля оставляем для формы ввода
    loading_address = models.TextField()
    unloading_address = models.TextField()

    # СВЯЗЬ С ПРИЛОЖЕНИЕМ ROUTES:
    route = models.ForeignKey(Route, on_delete=models.PROTECT, blank=True, null=True)

    weight = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def calculate_price(self):
        """
        Итоговая цена берет дистанцию из связанного Route
        """
        # Исправляем проверку: цена сбрасывается в 0, только если дистанция строго равна None или <= 0
        if not self.route or self.route.distance_km is None or self.route.distance_km <= 0:
            self.total_price = 0.00
            return

        distance = self.route.distance_km
        base_rate_per_km = 6.0
        cost_by_distance = base_rate_per_km * distance

        extra_charges = 0.0
        weight_tons = self.weight or 0.0
        volume_m3 = self.volume or 0.0

        if weight_tons > 0 and volume_m3 > 0:
            weight_kg = weight_tons * 1000
            density = weight_kg / volume_m3
            if density < 250:
                extra_charges = volume_m3 * 300.0
            else:
                extra_charges = weight_tons * 500.0
        elif weight_tons > 0:
            extra_charges = weight_tons * 500.0
        elif volume_m3 > 0:
            extra_charges = volume_m3 * 300.0

        self.total_price = round(cost_by_distance + extra_charges, 2)

    def save(self, *args, **kwargs):
        # Автоматически находим существующий или создаем новый маршрут в приложении routes
        if self.loading_address and self.unloading_address:
            # get_or_create вернет объект маршрута, даже если адреса введены с разным регистром
            route_obj, created = Route.objects.get_or_create(
                loading_address=self.loading_address.strip(),
                unloading_address=self.unloading_address.strip()
            )
            self.route = route_obj

        # Считаем цену на основе привязанного маршрута
        self.calculate_price()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class TripAssignment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    driver = models.ForeignKey(DriverProfile, on_delete=models.PROTECT)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    # Сюда можно добавить поле для фото документов от водителя
    closing_document_photo = models.ImageField(upload_to='trip_docs/', blank=True, null=True)

    class Meta:
        verbose_name = "Расчет маршрута"
        verbose_name_plural = "Расчет маршрута"


STATUS_MAPPING = {
    'created': 'Создан (в обработке)',
    'in_progress': 'В пути / Выполняется',
    'completed': 'Выполнен',
    'canceled': 'Отменён',
}


@receiver(post_save, sender=Order)
def order_status_changed_notification(sender, instance, created, **kwargs):

    if instance.client and instance.client.email:

        status_ru = STATUS_MAPPING.get(instance.status, instance.status)
        subject = f"Обновление статуса заказа №{instance.id} | TRANSPORT COMPANY"
        message = (
            f"Здравствуйте, {instance.client.full_name or instance.client.username}!\n\n"
            f"Статус вашего заказа №{instance.id} изменился на: \"{status_ru}\".\n\n"
            f"Посмотреть детали заказа вы можете в своем личном кабинете.\n"
            f"Спасибо, что выбираете нас!\n\n"
            f"С уважением, команда TRANSPORT COMPANY."
        )

        try:
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.client.email],
                fail_silently=True,  # Поставь True в продакшене, чтобы падение почты не ломало сайт
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")