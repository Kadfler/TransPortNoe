from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderCreateForm, OrderEditForm
from django.core.exceptions import PermissionDenied
from .models import Order, Client
from django import forms


@login_required(login_url='users:login')
def order_create(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Создаем или находим клиента по телефону (для общей базы контрагентов)
            client, created = Client.objects.get_or_create(
                contact_phone=form.cleaned_data['client_phone'],
                defaults={
                    'name': form.cleaned_data['client_name'],
                    'tax_profile': form.cleaned_data['tax_profile']
                }
            )

            # 2. Создаем сам заказ и привязываем его к ТЕКУЩЕМУ пользователю системы
            order = Order(
                client=request.user,  # Ссылаемся на CustomUser, как требует ForeignKey
                loading_address=form.cleaned_data['loading_address'],
                unloading_address=form.cleaned_data['unloading_address'],
                weight=form.cleaned_data['weight'],
                volume=form.cleaned_data['volume'],
                description=form.cleaned_data['description']
            )

            order.save()

            return redirect('main:catalog')
    else:
        form = OrderCreateForm()

    context = {
        'form': form,
        'header_theme': 'dark'
    }
    return render(request, 'orders/order_form.html', context)


@login_required(login_url='users:login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    is_driver = request.user.is_authenticated and getattr(request.user, 'role', None) == 'driver'

    # Проверяем автора заказа: просто сравниваем объекты пользователей!
    is_author = request.user.is_authenticated and (order.client == request.user)

    # Перестраховка: достаем телефоны максимально безопасно
    user_phone = getattr(request.user, 'phone', None)

    # Проверяем, где именно лежит телефон клиента — в связанном объекте или напрямую
    if hasattr(order.client, 'contact_phone'):
        client_phone = order.client.contact_phone
    else:
        client_phone = getattr(order.client, 'phone', None)

    # Сравниваем только если оба телефона успешно нашлись
    is_author = False
    if user_phone and client_phone:
        is_author = (str(user_phone).strip() == str(client_phone).strip())

    context = {
        'order': order,
        'is_driver': is_driver,
        'is_author': is_author,
        'header_theme': 'dark'
    }
    return render(request, 'orders/order_detail.html', context)


@login_required(login_url='users:login')
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Безопасная проверка автора по телефону (как у тебя в detail)
    user_phone = getattr(request.user, 'phone', None)
    client_phone = getattr(order.client, 'contact_phone', getattr(order.client, 'phone', None))

    if not user_phone or not client_phone or str(user_phone).strip() != str(client_phone).strip():
        return redirect('main:catalog')

    if request.method == 'POST':
        # Используем НОВУЮ форму редактирования
        form = OrderEditForm(request.POST)

        if form.is_valid():
            # Обновляем только разрешенные поля
            order.loading_address = form.cleaned_data.get('loading_address')
            order.unloading_address = form.cleaned_data.get('unloading_address')
            order.description = form.cleaned_data.get('description')
            order.weight = form.cleaned_data.get('weight')
            order.volume = form.cleaned_data.get('volume')

            order.distance_km = None

            order.save()
            return redirect('orders:order_detail', order_id=order.id)
    else:
        # Предзаполняем форму старыми данными заказа
        initial_data = {
            'loading_address': order.loading_address,
            'unloading_address': order.unloading_address,
            'description': order.description,
            'weight': order.weight,
            'volume': order.volume,
        }
        form = OrderEditForm(initial=initial_data)

    context = {
        'form': form,
        'order': order,
        'header_theme': 'dark',
        'is_edit': True
    }
    return render(request, 'orders/order_form.html', context)


@login_required(login_url='users:login')
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # БЕЗОПАСНАЯ ПРОВЕРКА АВТОРА
    user_phone = getattr(request.user, 'phone', None)
    if hasattr(order.client, 'contact_phone'):
        client_phone = order.client.contact_phone
    else:
        client_phone = getattr(order.client, 'phone', None)

    # Если телефоны не совпали — тихо возвращаем в каталог
    if not user_phone or not client_phone or str(user_phone).strip() != str(client_phone).strip():
        return redirect('main:catalog')

    # УДАЛЯЕМ СРАЗУ (без разницы, GET это или POST запрос)
    order.delete()

    # Добавим всплывающее уведомление, чтобы пользователь понял, что заказ стерт
    from django.contrib import messages
    messages.success(request, f"Заказ №{order_id} успешно удален.")

    return redirect('main:catalog')
