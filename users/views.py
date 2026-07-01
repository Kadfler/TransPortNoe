from django.contrib.auth import login
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from vehicles.models import Vehicle
from users.forms import RegisterForm, LoginForm
from .models import CustomUser
from .forms import ProfileEditForm
from orders.models import Order, TripAssignment, DriverProfile
from django.db.models.signals import post_save
from django.dispatch import receiver


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:catalog')
    else:
        form = LoginForm()

    context = {
        'form': form,
        'header_theme': 'dark'
    }
    return render(request, 'users/login.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:catalog')
    else:
        form = RegisterForm()

    context = {
        'form': form,
        'header_theme': 'dark'
    }
    return render(request, 'users/register.html', context)


@login_required
def manage_roles_view(request):
    if request.user.role not in ['admin', 'dispatcher']:
        return HttpResponseForbidden("У вас нет доступа к этой странице.")

    users_list = CustomUser.objects.exclude(role='admin').exclude(is_superuser=True).order_by('id')

    context = {
        'users_list': users_list,
        'header_theme': 'dark'
    }
    return render(request, 'users/manage_roles.html', context)


@login_required
def change_role_view(request, user_id):
    if request.user.role not in ['admin', 'dispatcher']:
        return HttpResponseForbidden("Действие запрещено.")

    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        new_role = request.POST.get('role')
        allowed_roles = ['client', 'dispatcher', 'driver', 'accountant']

        if new_role in allowed_roles:
            target_user.role = new_role
            target_user.save()

    return redirect('users:manage_roles')


class profile_view(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 1. Если это водитель — показываем его рейсы
        if user.role == 'driver':
            if hasattr(user, 'driver_profile'):
                context['assignments'] = TripAssignment.objects.filter(
                    driver=user.driver_profile
                ).select_related('order', 'vehicle', 'order__route').order_by('-id')
            else:
                context['assignments'] = []

        # 2. Для ВСЕХ остальных (клиенты, админы, диспетчеры)
        # показываем ТОЛЬКО их собственные заказы
        else:
            context['orders'] = Order.objects.filter(client=user).select_related('route').order_by('-id')

        return context


@method_decorator(require_POST, name='dispatch')
class cancel_order_view(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # ИСПРАВЛЕНО: Достаем pk из именованных аргументов пути (URL)
        order_id = kwargs.get('pk')

        try:
            order = Order.objects.get(id=order_id)

            if request.user.role in ['admin', 'dispatcher']:
                order.delete()
                messages.success(request, f"Заказ №{order_id} успешно удален администратором.")
            elif request.user.role == 'client' and order.client == request.user:
                if order.status == 'created':
                    order.delete()
                    messages.success(request, "Ваш заказ успешно отменен.")
                else:
                    messages.error(request,
                                   "Нельзя отменить заказ, к которому уже привязан водитель или который выполнен.")
            else:
                messages.error(request, "У вас нет прав для отмены этого заказа.")

        except Order.DoesNotExist:
            messages.error(request, "Указанный заказ не найден.")

        # ИСПРАВЛЕНО: Редирект на правильное пространство имен
        return redirect('users:profile')


@method_decorator(require_POST, name='dispatch')
class reject_assignment_view(LoginRequiredMixin, View):
    """
    Вьюха для обработки отказа ВОДИТЕЛЯ от рейса.
    Удаляет TripAssignment и возвращает статус заказа обратно в 'created'.
    """

    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')

        if request.user.role != 'driver' or not hasattr(request.user, 'driver_profile'):
            messages.error(request, "Только водители могут отказываться от назначенных рейсов.")
            return redirect('users:profile')

        assignment = get_object_or_404(TripAssignment, order_id=order_id, driver=request.user.driver_profile)

        # Получаем сам заказ, сбрасываем статус на 'created'
        order = assignment.order
        order.status = 'created'
        order.save()

        # Удаляем запись назначения водителя
        assignment.delete()

        messages.success(request, f"Вы успешно отказались от рейса №{order_id}. Заказ возвращен в обработку.")
        return redirect('users:profile')


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'users/profile_edit.html'

    def get(self, request, *args, **kwargs):
        form = ProfileEditForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('users:profile')

        return render(request, self.template_name, {'form': form})


@login_required
def logistics_management_view(request):
    if request.user.role not in ['admin', 'dispatcher']:
        return HttpResponseForbidden("У вас нет прав для доступа к этому разделу.")

    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        if action == 'assign':
            vehicle_id = request.POST.get('vehicle_id')
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)

            if not vehicle.driver:
                messages.error(request, f"У автомобиля {vehicle.mark} не назначен водитель!")
                return redirect('users:logistics')

            is_busy = TripAssignment.objects.filter(vehicle=vehicle).exclude(order=order).exists()
            if is_busy:
                messages.error(request,
                               f"Ошибка: Автомобиль {vehicle.mark} [{vehicle.plate_number}] уже находится в рейсе!")
                return redirect('users:logistics')

            TripAssignment.objects.update_or_create(
                order=order,
                defaults={
                    'vehicle': vehicle,
                    'driver': vehicle.driver.driver_profile,
                    'total_cost': order.total_price or 0.00
                }
            )

            Order.objects.filter(id=order.id).update(status='in_progress')
            messages.success(request, f"К заказу №{order_id} успешно привязан транспорт {vehicle.mark}.")

        elif action == 'unassign':
            # Удаляем связь с транспортом
            TripAssignment.objects.filter(order=order).delete()
            order.status = 'created'
            order.save()
            messages.success(request, f"Транспорт успешно отвязан от заказа №{order_id}.")



        elif action == 'complete':

            TripAssignment.objects.filter(order_id=order_id).delete()
            Order.objects.filter(id=order_id).update(status='completed')

            messages.success(request, f"Заказ №{order_id} переведен в статус 'Выполнен'.")

        return redirect('users:logistics')

    # Получаем заказы и доступный транспорт
    all_orders = Order.objects.select_related('route', 'client').order_by('-id')
    available_vehicles = Vehicle.objects.select_related('driver').exclude(driver__isnull=True)

    # Получаем все активные рейсы
    all_assignments = TripAssignment.objects.select_related('vehicle', 'vehicle__driver').all()

    # НОВАЯ СТРОКА: Собираем ID машин, которые сейчас в пути
    busy_vehicle_ids = [a.vehicle_id for a in all_assignments]

    # Создаем словарь для быстрого поиска: {order_id: assignment}
    assignments_dict = {a.order_id: a for a in all_assignments}

    # Вручную и аккуратно прокидываем данные в каждый заказ для шаблона
    for o in all_orders:
        assignment = assignments_dict.get(o.id)
        if assignment:
            o.display_truck = assignment.vehicle
            if assignment.vehicle and assignment.vehicle.driver:
                o.display_driver_name = assignment.vehicle.driver.full_name or assignment.vehicle.driver.username
        else:
            o.display_truck = None
            o.display_driver_name = None

    context = {
        'orders': all_orders,
        'vehicles': available_vehicles,
        'busy_vehicle_ids': busy_vehicle_ids,  # ПЕРЕДАЕМ В КОНТЕКСТ ШАБЛОНА
        'header_theme': 'dark',
        'active_tab': 'logistics'
    }
    return render(request, 'users/logistics.html', context)


@receiver(post_save, sender=CustomUser)
def create_or_save_driver_profile(sender, instance, created, **kwargs):
    if instance.role == 'driver':
        DriverProfile.objects.get_or_create(user=instance)
    else:
        DriverProfile.objects.filter(user=instance).delete()
