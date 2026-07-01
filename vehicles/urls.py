from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('list/', views.vehicle_list, name='vehicle_list'),
    path('create/', views.vehicle_create, name='vehicle_create'),
]