from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='home')),
    path('vehicles/', include('vehicles.urls', namespace='vehicles')),
    path('users/', include('users.urls', namespace='users')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('routes/', include('routes.urls', namespace='routes')),
    path('orders/', include('orders.urls', namespace='orders')),
]