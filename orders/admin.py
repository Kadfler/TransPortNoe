from django.contrib import admin
from .models import Client, Order, TripAssignment


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_phone', 'tax_profile')
    search_fields = ('name', 'contact_phone')
    list_filter = ('tax_profile',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Выводим основные данные, включая автоматически вычисляемую стоимость
    list_display = ('id', 'client', 'loading_address', 'unloading_address', 'weight', 'total_price')
    # Поиск по клиенту и адресам
    search_fields = ('client__full_name', 'loading_address', 'unloading_address')
    # Фильтр справа
    list_filter = ('client', 'route')

    # Делаем поле цены только для чтения, так как оно считается автоматически в save()
    readonly_fields = ('total_price', 'route')

