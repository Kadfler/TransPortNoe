from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('api/<int:route_id>/', views.route_geometry_api, name='route_api'),
]