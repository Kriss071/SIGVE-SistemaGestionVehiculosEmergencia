from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # Roles
    path('roles/', views.role_list_view, name='role_list'),
    
    # Empleados
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/create/', views.employee_create_view, name='employee_create'),
    path('employees/update/<uuid:employee_id>/', views.employee_update_view, name='employee_update'),
    path('employees/delete/<uuid:employee_id>/', views.employee_delete_view, name='employee_delete'),
    path('api/employees/<uuid:employee_id>/', views.get_employee_api, name='api_get_employee'),

    # Talleres
    path('workshops/', views.workshop_list_view, name='workshop_list'),
    path('workshops/create/', views.workshop_create_view, name='workshop_create'),
    path('workshops/update/<int:workshop_id>/', views.workshop_update_view, name='workshop_update'),
    path('workshops/delete/<int:workshop_id>/', views.workshop_delete_view, name='workshop_delete'),
    path('api/workshops/<int:workshop_id>/', views.get_workshop_api, name='api_get_workshop'),

    # Proveedores
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/create/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/update/<int:supplier_id>/', views.supplier_update_view, name='supplier_update'),
    path('suppliers/delete/<int:supplier_id>/', views.supplier_delete_view, name='supplier_delete'),
    path('api/suppliers/<int:supplier_id>/', views.get_supplier_api, name='api_get_supplier'),

    # Tipos de Vehículo
    path('vehicle-types/', views.vehicle_type_list_view, name='vehicle_type_list'),
    path('vehicle-types/create/', views.vehicle_type_create_view, name='vehicle_type_create'),
    path('vehicle-types/update/<int:vehicle_type_id>/', views.vehicle_type_update_view, name='vehicle_type_update'),
    path('vehicle-types/delete/<int:vehicle_type_id>/', views.vehicle_type_delete_view, name='vehicle_type_delete'),
    path('api/vehicle-types/<int:vehicle_type_id>/', views.get_vehicle_type_api, name='api_get_vehicle_type'),

    # Cuartel de Bombero
    path('fire_stations/', views.fire_station_list_view, name='fire_station_list'),
    path('fire_stations/create/', views.fire_station_create_view, name='fire_station_create'),
    path('fire_stations/update/<int:fire_station_id>/', views.fire_station_update_view, name='fire_station_update'),
    path('fire_stations/delete/<int:fire_station_id>/', views.fire_station_delete_view, name='fire_station_delete'),
    path('api/fire_stations/<int:fire_station_id>/', views.get_fire_station_api, name='api_get_fire_station'),

    # Estados de Vehículos
    path('vehicle-statuses/', views.vehicle_status_list_view, name='vehicle_status_list'),
    path('vehicle-statuses/create/', views.vehicle_status_create_view, name='vehicle_status_create'),
    path('vehicle-statuses/update/<int:vehicle_status_id>/', views.vehicle_status_update_view, name='vehicle_status_update'),
    path('vehicle-statuses/delete/<int:vehicle_status_id>/', views.vehicle_status_delete_view, name='vehicle_status_delete'),
    path('api/vehicle-statuses/<int:vehicle_status_id>/', views.get_vehicle_status_api, name='api_get_vehicle_status'),

    # Tipo de Combustible
    path('fuel-types/', views.fuel_type_list_view, name='fuel_type_list'),
    path('fuel-types/create/', views.fuel_type_create_view, name='fuel_type_create'),
    path('fuel-types/update/<int:fuel_type_id>/', views.fuel_type_update_view, name='fuel_type_update'),
    path('fuel-types/delete/<int:fuel_type_id>/', views.fuel_type_delete_view, name='fuel_type_delete'),
    path('api/fuel-types/<int:fuel_type_id>/', views.get_fuel_type_api, name='api_get_fuel_type'),

    # Tipo de Transmisión
    path('transmission-types/', views.transmission_type_list_view, name='transmission_type_list'),
    path('transmission-types/create/', views.transmission_type_create_view, name='transmission_type_create'),
    path('transmission-types/update/<int:transmission_type_id>/', views.transmission_type_update_view, name='transmission_type_update'),
    path('transmission-types/delete/<int:transmission_type_id>/', views.transmission_type_delete_view, name='transmission_type_delete'),
    path('api/transmission-types/<int:transmission_type_id>/', views.get_transmission_type_api, name='api_get_transmission_type'),

    # Tipo de Aceite
    path('oil-types/', views.oil_type_list_view, name='oil_type_list'),
    path('oil-types/create/', views.oil_type_create_view, name='oil_type_create'),
    path('oil-types/update/<int:oil_type_id>/', views.oil_type_update_view, name='oil_type_update'),
    path('oil-types/delete/<int:oil_type_id>/', views.oil_type_delete_view, name='oil_type_delete'),
    path('api/oil-types/<int:oil_type_id>/', views.get_oil_type_api, name='api_get_oil_type'),

    # Tipo de Refigerante
    path('coolant-types/', views.coolant_type_list_view, name='coolant_type_list'),
    path('coolant-types/create/', views.coolant_type_create_view, name='coolant_type_create'),
    path('coolant-types/update/<int:coolant_type_id>/', views.coolant_type_update_view, name='coolant_type_update'),
    path('coolant-types/delete/<int:coolant_type_id>/', views.coolant_type_delete_view, name='coolant_type_delete'),
    path('api/coolant-types/<int:coolant_type_id>/', views.get_coolant_type_api, name='api_get_coolant_type'),
]