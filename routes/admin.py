from django.contrib import admin
from .models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    # Что отображать в таблице списка маршрутов
    list_display = ('id', 'loading_address', 'unloading_address', 'distance_km', 'created_at')

    # Клик по какому полю открывает детальный просмотр/редактирование
    list_display_links = ('id', 'loading_address', 'unloading_address')

    # Поиск по адресам погрузки и выгрузки
    search_fields = ('loading_address', 'unloading_address')

    # Фильтр справа по дате создания маршрутов
    list_filter = ('created_at',)

    # Защищаем поля автоматического расчета от случайного редактирования руками
    readonly_fields = ('distance_km', 'loading_lat', 'loading_lon', 'unloading_lat', 'unloading_lon', 'created_at')

    # Группируем поля внутри карточки маршрута для красивого визуального разделения
    fieldsets = (
        ('Основная информация', {
            'fields': ('loading_address', 'unloading_address')
        }),
        ('Автоматически рассчитанные данные', {
            'fields': ('distance_km', 'created_at'),
            'classes': ('collapse',),  # По желанию эту группу можно сделать сворачиваемой
        }),
        ('Гео-координаты для карт', {
            'fields': (('loading_lat', 'loading_lon'), ('unloading_lat', 'unloading_lon')),
            'description': 'Координаты определяются автоматически через сервис Nominatim при сохранении.',
        }),
    )