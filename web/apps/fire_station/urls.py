from django.urls import path
from . import views

app_name = 'fire_station'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de Vehículos
    path('vehicles/', views.vehicles_list, name='vehicles_list'),
    path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:vehicle_id>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:vehicle_id>/delete/', views.vehicle_delete, name='vehicle_delete'),
    
    # Gestión de Usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/<str:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<str:user_id>/deactivate/', views.user_deactivate, name='user_deactivate'),
    path('users/<str:user_id>/activate/', views.user_activate, name='user_activate'),
    
    # API Endpoints
    path('api/vehicles/<int:vehicle_id>/', views.api_get_vehicle, name='api_get_vehicle'),
    path('api/users/<str:user_id>/', views.api_get_user, name='api_get_user'),
]

