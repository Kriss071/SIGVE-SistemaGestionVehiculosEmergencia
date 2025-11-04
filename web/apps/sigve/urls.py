from django.urls import path
from . import views

app_name = 'sigve'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Centro de Solicitudes
    path('requests/', views.requests_center, name='requests_center'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    
    # Gestión de Talleres
    path('workshops/', views.workshops_list, name='workshops_list'),
    path('workshops/create/', views.workshop_create, name='workshop_create'),
    path('workshops/<int:workshop_id>/edit/', views.workshop_edit, name='workshop_edit'),
    path('workshops/<int:workshop_id>/delete/', views.workshop_delete, name='workshop_delete'),
    
    # Gestión de Cuarteles
    path('fire-stations/', views.fire_stations_list, name='fire_stations_list'),
    path('fire-stations/create/', views.fire_station_create, name='fire_station_create'),
    path('fire-stations/<int:fire_station_id>/edit/', views.fire_station_edit, name='fire_station_edit'),
    path('fire-stations/<int:fire_station_id>/delete/', views.fire_station_delete, name='fire_station_delete'),
    
    # Gestión de Repuestos
    path('spare-parts/', views.spare_parts_list, name='spare_parts_list'),
    path('spare-parts/create/', views.spare_part_create, name='spare_part_create'),
    path('spare-parts/<int:spare_part_id>/edit/', views.spare_part_edit, name='spare_part_edit'),
    path('spare-parts/<int:spare_part_id>/delete/', views.spare_part_delete, name='spare_part_delete'),
    
    # Gestión de Proveedores
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Catálogos Genéricos
    path('catalogs/<str:catalog_name>/', views.catalog_list, name='catalog_list'),
    path('catalogs/<str:catalog_name>/create/', views.catalog_create, name='catalog_create'),
    path('catalogs/<str:catalog_name>/<int:item_id>/edit/', views.catalog_edit, name='catalog_edit'),
    path('catalogs/<str:catalog_name>/<int:item_id>/delete/', views.catalog_delete, name='catalog_delete'),
    
    # Gestión de Usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/<str:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<str:user_id>/deactivate/', views.user_deactivate, name='user_deactivate'),
    
    # API Endpoints
    path('api/communes/', views.api_get_communes, name='api_get_communes'),
    path('api/workshops/<int:workshop_id>/', views.api_get_workshop, name='api_get_workshop'),
    path('api/fire-stations/<int:fire_station_id>/', views.api_get_fire_station, name='api_get_fire_station'),
    path('api/spare-parts/<int:spare_part_id>/', views.api_get_spare_part, name='api_get_spare_part'),
]


