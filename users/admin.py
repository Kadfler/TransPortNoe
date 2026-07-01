from django.contrib import admin
from .models import CustomUser, DriverProfile


# 1. Создаем Inline-класс для профиля водителя.
# Благодаря этому профиль будет отображаться прямо внутри карточки пользователя.
class DriverProfileInline(admin.StackedInline):
    model = DriverProfile
    can_delete = False  # Запрещаем случайно удалить профиль отдельно от юзера
    verbose_name = "Дополнительный профиль водителя"
    verbose_name_plural = "Дополнительные профили водителей"
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Подключаем наш Inline блок к админке пользователя
    inlines = (DriverProfileInline,)

    # Колонки в общем списке
    list_display = ('id', 'username', 'full_name', 'role', 'phone', 'email')

    # Быстрые фильтры справа
    list_filter = ('role',)

    # Поиск по челику
    search_fields = ('username', 'full_name', 'phone')

    # Карточка пользователя (когда заходишь внутрь)
    fields = ('username', 'full_name', 'role', 'phone', 'email', 'is_active')


# Оставляем отдельную админку для профилей, если захочется смотреть их общим списком
@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'license_number', 'status')
    list_filter = ('status',)
    search_fields = ('user__full_name', 'license_number')