from django.urls import path
from . import views

app_name = 'workshop'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de Órdenes de Mantención
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update/', views.order_update, name='order_update'),
    
    # Gestión de Tareas
    path('orders/<int:order_id>/tasks/create/', views.task_create, name='task_create'),
    path('orders/<int:order_id>/tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    
    # Gestión de Repuestos en Tareas
    path('orders/<int:order_id>/parts/add/', views.part_add_to_task, name='part_add_to_task'),
    path('orders/<int:order_id>/parts/<int:part_id>/remove/', views.part_remove_from_task, name='part_remove_from_task'),
    
    # Gestión de Inventario
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_add, name='inventory_add'),
    path('inventory/<int:inventory_id>/update/', views.inventory_update, name='inventory_update'),
    path('inventory/<int:inventory_id>/delete/', views.inventory_delete, name='inventory_delete'),
    
    # Gestión de Proveedores
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Gestión de Empleados (Solo Admin Taller)
    path('employees/', views.employees_list, name='employees_list'),
    path('employees/<str:user_id>/update/', views.employee_update, name='employee_update'),
    path('employees/<str:user_id>/deactivate/', views.employee_deactivate, name='employee_deactivate'),
    path('employees/<str:user_id>/activate/', views.employee_activate, name='employee_activate'),
]



