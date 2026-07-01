from django import forms

class OrderCreateForm(forms.Form):

    client_name = forms.CharField(label='Название компании / ФИО заказчика', max_length=255, widget=forms.TextInput(attrs={'placeholder': 'ООО Вектор / Иванов И.И.'}))
    client_phone = forms.CharField(label='Контактный телефон', max_length=20, widget=forms.TextInput(attrs={'placeholder': '8(999)123-45-67'}))
    tax_profile = forms.ChoiceField(label='Налоговый профиль', choices=[('НДС', 'НДС'), ('без НДС', 'без НДС')], widget=forms.Select())

    weight = forms.FloatField(
        label='Вес груза (тонн)',
        widget=forms.NumberInput(attrs={'placeholder': '25', 'step': '0.1'})
    )
    volume = forms.FloatField(
        label='Объем груза (м³)',
        widget=forms.NumberInput(attrs={'placeholder': '150', 'step': '0.1'})
    )

    loading_address = forms.CharField(label='Адрес погрузки', widget=forms.TextInput(attrs={'placeholder': 'Москва, ул. Пушкина, д. 10'}))
    unloading_address = forms.CharField(label='Адрес выгрузки', widget=forms.TextInput(attrs={'placeholder': 'Санкт-Петербург, ул. Красная, д. 5'}))
    description = forms.CharField(label='Описание груза', widget=forms.Textarea(attrs={'placeholder': 'Продукты питания, 20 паллет...', 'rows': 3}), required=False) # Сделаем необязательным, раз есть вес

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class OrderEditForm(forms.Form):
    weight = forms.FloatField(label='Вес груза (тонн)', widget=forms.NumberInput(attrs={'step': '0.1'}))
    volume = forms.FloatField(label='Объем груза (м³)', widget=forms.NumberInput(attrs={'step': '0.1'}))
    loading_address = forms.CharField(label='Адрес погрузки', widget=forms.TextInput())
    unloading_address = forms.CharField(label='Адрес выгрузки', widget=forms.TextInput())
    description = forms.CharField(label='Описание груза', widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})