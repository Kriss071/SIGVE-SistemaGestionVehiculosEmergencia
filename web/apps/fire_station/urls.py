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
    path('vehicles/<int:vehicle_id>/history/', views.vehicle_history, name='vehicle_history'),
    
    # Gestión de Usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<str:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<str:user_id>/deactivate/', views.user_deactivate, name='user_deactivate'),
    path('users/<str:user_id>/activate/', views.user_activate, name='user_activate'),
    
    # Solicitudes de Mantenimiento
    path('requests/', views.requests_list, name='requests_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/cancel/', views.request_cancel, name='request_cancel'),
    
    # API Endpoints
    path('api/vehicles/<int:vehicle_id>/', views.api_get_vehicle, name='api_get_vehicle'),
    path('api/users/<str:user_id>/', views.api_get_user, name='api_get_user'),
    path('api/requests/<int:request_id>/', views.api_get_request, name='api_get_request'),
]

