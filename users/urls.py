import profile

from django.urls import path
from django.contrib.auth import views as auth_views
from users.views import login_view, register_view, manage_roles_view, change_role_view, profile_view, cancel_order_view,reject_assignment_view, ProfileEditView, logistics_management_view

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile_view.as_view(), name='profile'),
    path('order/<int:pk>/cancel/', cancel_order_view.as_view(), name='cancel_order'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('assignment/<int:pk>/reject/', reject_assignment_view.as_view(), name='reject_assignment'),
    path('logistics/', logistics_management_view, name='logistics'),

    path('manage-roles/', manage_roles_view, name='manage_roles'),
    path('change-role/<int:user_id>/', change_role_view, name='change_role'),
]
