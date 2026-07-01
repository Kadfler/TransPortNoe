from django import forms
from vehicles.models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        # Перечисляем все поля из твоей модели
        fields = [
            'mark', 'plate_number', 'body_type',
            'capacity', 'base_rate_per_km', 'mileage', 'driver'
        ]

        # Переводим названия полей на русский язык
        labels = {
            'mark': 'Марка и модель',
            'plate_number': 'Государственный номер',
            'body_type': 'Тип кузова',
            'capacity': 'Грузоподъемность (тонн)',
            'base_rate_per_km': 'Ставка за км (₽)',
            'mileage': 'Текущий пробег (км)',
            'driver': 'Назначенный водитель',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Навешиваем стили на все поля, кроме чекбоксов
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs['class'] = 'form-control'