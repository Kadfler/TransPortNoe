from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.doc_list, name='doc_list'),
    path('create/', views.doc_create, name='doc_create'),
    path('<int:pk>/', views.doc_detail, name='doc_detail'),
]