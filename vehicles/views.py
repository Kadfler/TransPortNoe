from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from vehicles.models import Vehicle
from .forms import VehicleForm
from orders.models import TripAssignment

def vehicle_list(request):
    # Стартовый QuerySet только активных машин
    vehicles_queryset = Vehicle.objects.filter(is_active=True).select_related('driver__driver_profile')

    # Получаем ID всех машин, которые сейчас в рейсе
    busy_vehicle_ids = list(TripAssignment.objects.values_list('vehicle_id', flat=True))

    # --- 1. ПОИСК ПО МАРКЕ ИЛИ ГОСНОМЕРУ ---
    search_query = request.GET.get('search_vehicle', '').strip()
    if search_query:
        vehicles_queryset = vehicles_queryset.filter(
            Q(mark__icontains=search_query) | Q(plate_number__icontains=search_query)
        )

    # --- 2. ФИЛЬТР ПО ТИПУ КУЗОВА ---
    body_type_filter = request.GET.get('body_type', '').strip()
    if body_type_filter:
        vehicles_queryset = vehicles_queryset.filter(body_type=body_type_filter)

    # --- 3. ФИЛЬТР ПО ГРУЗОПОДЪЕМНОСТИ ---
    capacity_filter = request.GET.get('capacity_range', '').strip()
    if capacity_filter:
        if capacity_filter == 'light':      # Малотоннажные до 3.5 т
            vehicles_queryset = vehicles_queryset.filter(capacity__lt=3.5)
        elif capacity_filter == 'medium':   # Средние от 3.5 до 10 т
            vehicles_queryset = vehicles_queryset.filter(capacity__gte=3.5, capacity__lte=10)
        elif capacity_filter == 'heavy':    # Фуры / Тяжелые от 10 т
            vehicles_queryset = vehicles_queryset.filter(capacity__gt=10)

    # --- 4. ФИЛЬТР ПО СТАТУСУ ЗАНЯТОСТИ ---
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        vehicles_list_filtered = list(vehicles_queryset)
        if status_filter == 'busy':
            vehicles_list_filtered = [v for v in vehicles_list_filtered if v.id in busy_vehicle_ids]
        elif status_filter == 'free':
            vehicles_list_filtered = [v for v in vehicles_list_filtered if v.id not in busy_vehicle_ids]
        vehicles_list = vehicles_list_filtered
    else:
        vehicles_list = list(vehicles_queryset)

    # --- 5. ПАГИНАЦИЯ ---
    # Выводим по 6 машин на страницу
    paginator = Paginator(vehicles_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'vehicles': page_obj,  # Передаем объект страницы с пагинацией
        'busy_vehicle_ids': busy_vehicle_ids,
        'filters': {
            'search_vehicle': search_query,
            'body_type': body_type_filter,
            'capacity_range': capacity_filter,
            'status': status_filter,
        }
    }
    return render(request, 'vehicles/vehicle_list.html', context)

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle})


def vehicle_create(request):
    # Защита от клиентов
    if request.user.is_authenticated and request.user.role == 'client':
        return redirect('vehicles:vehicle_list')

    # Проверяем, является ли пользователь обычным водителем
    is_only_driver = request.user.role == 'driver'

    if request.method == 'POST':
        form = VehicleForm(request.POST)

        # Если это водитель, убираем поле из обязательной валидации формы
        if is_only_driver:
            form.errors.pop('driver', None)

        if form.is_valid():
            vehicle = form.save(commit=False)

            # Принудительно пишем водителем текущего юзера
            if is_only_driver:
                vehicle.driver = request.user

            vehicle.save()
            return redirect('vehicles:vehicle_list')
    else:
        initial_data = {}
        if is_only_driver:
            initial_data['driver'] = request.user

        form = VehicleForm(initial=initial_data)

    return render(request, 'vehicles/vehicle_create.html', {
        'form': form,
        'is_edit': False,
        'is_only_driver': is_only_driver,  # Передаем флаг в HTML шаблон
    })