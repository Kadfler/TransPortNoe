from django.db import models
import requests
from geopy.geocoders import Nominatim

class Route(models.Model):
    loading_address = models.TextField(verbose_name="Адрес погрузки")
    unloading_address = models.TextField(verbose_name="Адрес выгрузки")

    loading_lat = models.FloatField(blank=True, null=True, verbose_name="Широта погрузки")
    loading_lon = models.FloatField(blank=True, null=True, verbose_name="Долгота погрузки")
    unloading_lat = models.FloatField(blank=True, null=True, verbose_name="Широта выгрузки")
    unloading_lon = models.FloatField(blank=True, null=True, verbose_name="Долгота выгрузки")
    distance_km = models.FloatField(blank=True, null=True, verbose_name="Расстояние (км)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self):
        return f"{self.loading_address} -> {self.unloading_address} ({self.distance_km} км)"

    def save(self, *args, **kwargs):
        self.loading_address = self.loading_address.strip()
        self.unloading_address = self.unloading_address.strip()

        # Теперь проверяем на None
        if self.distance_km is None or not self.loading_lat:
            try:
                geolocator = Nominatim(user_agent="transport_routes_app_v1", timeout=10)
                loc1 = geolocator.geocode(self.loading_address)
                loc2 = geolocator.geocode(self.unloading_address)

                if loc1 and loc2:
                    self.loading_lat, self.loading_lon = loc1.latitude, loc1.longitude
                    self.unloading_lat, self.unloading_lon = loc2.latitude, loc2.longitude

                    url = f"http://router.project-osrm.org/route/v1/driving/{self.loading_lon},{self.loading_lat};{self.unloading_lon},{self.unloading_lat}?overview=false"
                    response = requests.get(url, timeout=5).json()

                    if response.get('code') == 'Ok':
                        self.distance_km = round(response['routes'][0]['distance'] / 1000, 1)
                        print(f"[ROUTES] Новый маршрут просчитан: {self.distance_km} км")
                    else:
                        self.distance_km = 150.0  # РЕЗЕРВ: если API доступно, но маршрут не построился
                else:
                    self.distance_km = 100.0  # РЕЗЕРВ: если адреса не нашлись на карте
            except Exception as e:
                print(f"[ROUTES КРИТ] Ошибка при создании маршрута: {e}")
                self.distance_km = 120.0  # РЕЗЕРВ: если вообще лег интернет или упал Nominatim

        super().save(*args, **kwargs)