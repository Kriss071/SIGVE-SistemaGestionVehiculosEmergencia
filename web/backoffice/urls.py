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
    # API para Empleados (NUEVO)
    path('api/employees/<uuid:employee_id>/', views.get_employee_api, name='api_get_employee'),
]