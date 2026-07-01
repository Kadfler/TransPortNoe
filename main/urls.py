from django.urls import path
from . import views

app_name = 'main'

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('documents/', views.documents, name='documents'),
    path('transport/', views.transport, name='transport'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
path('price/', views.price_view, name='price'),
]