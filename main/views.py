from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.db.models import Sum
from django.shortcuts import render
from django.core.paginator import Paginator
from orders.models import Order
from users.models import DriverProfile
from vehicles.models import Vehicle

User = get_user_model()


def index(request):
    users_count = User.objects.count()
    drivers_count = DriverProfile.objects.count()
    vehicles_count = Vehicle.objects.count()
    total_orders_count = Order.objects.count()
    completed_orders_count = Order.objects.filter(status='completed').count()

    context = {
        'users_count': users_count,
        'drivers_count': drivers_count,
        'vehicles_count': vehicles_count,
        'total_orders_count': total_orders_count,  # Передаем в шаблон
        'completed_orders_count': completed_orders_count,  # Передаем в шаблон
        'header_theme': 'transparent',
    }
    return render(request, 'main/index.html', context)


def price_view(request):
    return render(request, 'main/price.html')


def catalog(request):
    # Получаем базовый QuerySet
    orders_queryset = Order.objects.all().order_by('-id')

    # --- 1. ПОИСК ПО ГОРОДУ НАЗНАЧЕНИЯ (Адрес Б) ---
    search_query = request.GET.get('search_city', '').strip()
    if search_query:
        orders_queryset = orders_queryset.filter(unloading_address__icontains=search_query)

    # --- 2. ФИЛЬТРАЦИЯ ПО СТАТУСУ ---
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        orders_queryset = orders_queryset.filter(status=status_filter)

    # --- 3. ФИЛЬТРАЦИЯ ПО ДАТЕ СОЗДАНИЯ ---
    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        # Предполагаем, что поле даты называется created_at (замени на свое, если нужно)
        orders_queryset = orders_queryset.filter(created_at__date=date_filter)

    # --- 4. ФИЛЬТРАЦИЯ ПО ВЕСОВОЙ КАТЕГОРИИ ---
    weight_filter = request.GET.get('weight_range', '').strip()
    if weight_filter:
        if weight_filter == 'light':       # до 3.5 тонн
            orders_queryset = orders_queryset.filter(weight__lt=3.5)
        elif weight_filter == 'medium':    # от 3.5 до 10 тонн
            orders_queryset = orders_queryset.filter(weight__gte=3.5, weight__lte=10)
        elif weight_filter == 'heavy':     # более 10 тонн
            orders_queryset = orders_queryset.filter(weight__gt=10)

    # Логика автоматического просчета цен, которая у тебя была
    for order in orders_queryset:
        if not order.total_price or (order.route and not order.route.distance_km):
            if hasattr(order, 'calculate_price'):
                order.calculate_price()
                order.save()

    # --- 5. ПАГИНАЦИЯ ---
    # Выводим по 6 заказов на страницу (можешь изменить число)
    paginator = Paginator(orders_queryset, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_driver = request.user.is_authenticated and request.user.role == 'driver'

    # Сохраняем текущие фильтры, чтобы передать их обратно в форму для отображения
    context = {
        'orders': page_obj,  # Теперь передаем объект страницы вместо сырого QuerySet
        'is_driver': is_driver,
        'header_theme': 'dark',
        # Возвращаем параметры, чтобы инпуты в форме не сбрасывались после отправки
        'filters': {
            'search_city': search_query,
            'status': status_filter,
            'date': date_filter,
            'weight_range': weight_filter,
        }
    }
    return render(request, 'orders/catalog.html', context)


def documents(request):
    return render(request, 'documents/documents.html')


def transport(request):
    return render(request, 'vehicles/transport.html')


def login_view(request):
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('main:index')  # Фикс имени (было home:index)