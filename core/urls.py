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

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
handler403 = 'django.views.defaults.permission_denied'
handler400 = 'django.views.defaults.bad_request'