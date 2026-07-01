from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'mark', 'plate_number', 'body_type', 'capacity', 'driver', 'is_active')
    list_filter = ('body_type', 'is_active')
    search_fields = ('mark', 'plate_number', 'driver__full_name')
    list_editable = ('is_active',) # Можно активировать/деактивировать прямо из списка