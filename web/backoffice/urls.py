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
]