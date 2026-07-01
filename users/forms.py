from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import CustomUser

User = get_user_model()


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '^[А-Яа-яЁё\s]+$',  # Запрещает цифры и латиницу в браузере
            'title': 'Введите ФИО используя только кириллицу',
            'placeholder': 'Иванов Иван Иванович'
        })
    )

    def clean_full_name(self):
        data = self.cleaned_data['full_name']
        # Проверка на сервере через регулярное выражение
        if not re.match(r'^[А-Яа-яЁё\s]+$', data):
            raise ValidationError("ФИО должно содержать только кириллицу.")
        return data

    phone = forms.CharField(
        label='Телефон',
        max_length=16
    )

    email = forms.EmailField(
        label='Email'
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Введите логин'
        })

        self.fields['full_name'].widget.attrs.update({
            'placeholder': 'Иванов Иван Иванович'
        })

        self.fields['phone'].widget.attrs.update({
            'placeholder': '8(999)123-45-67'
        })

        self.fields['email'].widget.attrs.update({
            'placeholder': 'example@mail.ru'
        })

        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('full_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            return user

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not re.fullmatch(r'[A-Za-z0-9]+', username):
            raise ValidationError('Логин должен содержать только латинские буквы и цифры')

        if len(username) < 6:
            raise ValidationError('Логин должен быть не короче 6 символов')

        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')

        if not re.fullmatch(r'[А-Яа-яЁё\s]+', full_name):
            raise ValidationError('ФИО должно содержать только кириллицу и пробелы')

        return full_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not re.fullmatch(r'8\(\d{3}\)\d{3}-\d{2}-\d{2}', phone):
            raise ValidationError('Телефон должен быть в формате 8(XXX)XXX-XX-XX')

        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с такой электронной почтой уже существует')

        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        max_length=150
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )

    error_messages = {
        'invalid_login': 'Неверный логин или пароль',
        'inactive': 'Учётная запись отключена'
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control rounded-pill px-3 py-2',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control rounded-pill px-3 py-2',
                'placeholder': 'example@mail.ru'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control rounded-pill px-3 py-2',
                'placeholder': '+7 (999) 999-99-99'
            }),
        }
        labels = {
            'full_name': 'ФИО / Название организации',
            'email': 'Email адрес',
            'phone': 'Номер телефона',
        }