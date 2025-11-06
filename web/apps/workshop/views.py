import logging
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .decorators import require_workshop_user, require_admin_taller
from .services.dashboard_service import DashboardService
from .services.order_service import OrderService
from .services.inventory_service import InventoryService
from .services.supplier_service import SupplierService
from .services.employee_service import EmployeeService
from .services.vehicle_service import VehicleService
from apps.sigve.services.workshop_service import WorkshopService
from .forms import (
    VehicleSearchForm, VehicleCreateForm, MaintenanceOrderForm,
    MaintenanceTaskForm, TaskPartForm, InventoryAddForm,
    InventoryUpdateForm, SupplierForm, EmployeeForm
)

logger = logging.getLogger(__name__)


# ===== DASHBOARD DEL TALLER =====

@require_workshop_user
def dashboard(request):
    """Vista principal del panel del taller."""
    workshop_id = request.workshop_id
    
    logger.debug("================================================")
    logger.debug(f"Dashboard Workshop, workshop_id: '{workshop_id}'")

    workshop_details = WorkshopService.get_workshop(workshop_id)
    workshop_name = workshop_details.get('name') if workshop_details else "Nombre Taller No Disponible"

    # Se obtiene los detalles del taller usando el servicio
    context = {
        'page_title': 'Dashboard Taller',
        'active_page': 'dashboard',
        'workshop_name': workshop_name
    }
    
    # Obtener estadísticas
    stats = DashboardService.get_statistics(workshop_id)
    context.update(stats)
    
    # Obtener órdenes activas (en taller)
    context['active_orders'] = DashboardService.get_active_orders(workshop_id, limit=10)
    
    return render(request, 'workshop/dashboard.html', context)


# ===== GESTIÓN DE ÓRDENES DE MANTENCIÓN =====

@require_workshop_user
def orders_list(request):
    """Lista de órdenes de mantención del taller con filtros."""
    workshop_id = request.workshop_id
    
    # Obtener filtros
    filters = {}
    if request.GET.get('status_id'):
        filters['status_id'] = request.GET.get('status_id')
    if request.GET.get('license_plate'):
        filters['license_plate'] = request.GET.get('license_plate')
    if request.GET.get('fire_station_id'):
        filters['fire_station_id'] = request.GET.get('fire_station_id')
    
    context = {
        'page_title': 'Órdenes de Mantención',
        'active_page': 'orders',
        'orders': OrderService.get_all_orders(workshop_id, filters),
        'order_statuses': VehicleService.get_order_statuses(),
        'fire_stations': VehicleService.get_all_fire_stations(),
        'filters': filters
    }
    
    return render(request, 'workshop/orders_list.html', context)


@require_workshop_user
def order_create(request):
    """Vista para crear una nueva orden de mantención."""
    workshop_id = request.workshop_id
    
    if request.method == 'POST':
        # Paso 1: Buscar o crear vehículo
        action = request.POST.get('action')
        
        if action == 'search_vehicle':
            form = VehicleSearchForm(request.POST)
            if form.is_valid():
                license_plate = form.cleaned_data['license_plate']
                vehicle = VehicleService.search_vehicle(license_plate)
                
                if vehicle:
                    # Vehículo encontrado, mostrar formulario de orden
                    context = {
                        'page_title': 'Nueva Orden de Mantención',
                        'active_page': 'orders',
                        'vehicle': vehicle,
                        'maintenance_types': VehicleService.get_maintenance_types(),
                        'order_statuses': VehicleService.get_order_statuses(),
                        'mechanics': EmployeeService.get_mechanics(workshop_id),
                        'step': 'create_order'
                    }
                    return render(request, 'workshop/order_create.html', context)
                else:
                    # Vehículo no encontrado, mostrar formulario de creación
                    context = {
                        'page_title': 'Nueva Orden de Mantención',
                        'active_page': 'orders',
                        'license_plate': license_plate,
                        'catalog_data': VehicleService.get_catalog_data(),
                        'fire_stations': VehicleService.get_all_fire_stations(),
                        'step': 'create_vehicle'
                    }
                    return render(request, 'workshop/order_create.html', context)
        
        elif action == 'create_vehicle':
            form = VehicleCreateForm(request.POST)
            if form.is_valid():
                vehicle_data = {
                    'license_plate': form.cleaned_data['license_plate'],
                    'brand': form.cleaned_data['brand'],
                    'model': form.cleaned_data['model'],
                    'year': form.cleaned_data['year'],
                    'fire_station_id': form.cleaned_data['fire_station_id'],
                    'vehicle_type_id': form.cleaned_data['vehicle_type_id'],
                    'engine_number': form.cleaned_data.get('engine_number'),
                    'vin': form.cleaned_data.get('vin'),
                    'fuel_type_id': form.cleaned_data.get('fuel_type_id'),
                    'transmission_type_id': form.cleaned_data.get('transmission_type_id')
                }
                
                vehicle = VehicleService.create_vehicle(vehicle_data)
                
                if vehicle:
                    messages.success(request, f'✅ Vehículo {vehicle["license_plate"]} registrado correctamente.')
                    # Mostrar formulario de orden
                    context = {
                        'page_title': 'Nueva Orden de Mantención',
                        'active_page': 'orders',
                        'vehicle': vehicle,
                        'maintenance_types': VehicleService.get_maintenance_types(),
                        'order_statuses': VehicleService.get_order_statuses(),
                        'mechanics': EmployeeService.get_mechanics(workshop_id),
                        'step': 'create_order'
                    }
                    return render(request, 'workshop/order_create.html', context)
                else:
                    messages.error(request, '❌ Error al registrar el vehículo.')
        
        elif action == 'create_order':
            form = MaintenanceOrderForm(request.POST)
            if form.is_valid():
                order_data = {
                    'vehicle_id': form.cleaned_data['vehicle_id'],
                    'mileage': form.cleaned_data['mileage'],
                    'maintenance_type_id': form.cleaned_data['maintenance_type_id'],
                    'order_status_id': form.cleaned_data['order_status_id'],
                    'assigned_mechanic_id': form.cleaned_data.get('assigned_mechanic_id') or None,
                    'entry_date': form.cleaned_data.get('entry_date', datetime.now().date()).isoformat(),
                    'observations': form.cleaned_data.get('observations', '')
                }
                
                order = OrderService.create_order(workshop_id, order_data)
                
                if order:
                    messages.success(request, f'✅ Orden de mantención #{order["id"]} creada correctamente.')
                    return redirect('workshop:order_detail', order_id=order['id'])
                else:
                    messages.error(request, '❌ Error al crear la orden de mantención.')
    
    # GET request: mostrar formulario inicial
    context = {
        'page_title': 'Nueva Orden de Mantención',
        'active_page': 'orders',
        'step': 'search_vehicle'
    }
    
    return render(request, 'workshop/order_create.html', context)


@require_workshop_user
def order_detail(request, order_id):
    """Vista detallada de una orden de mantención (ficha de trabajo)."""
    workshop_id = request.workshop_id
    
    order = OrderService.get_order(order_id, workshop_id)
    
    if not order:
        messages.error(request, '❌ Orden no encontrada o no pertenece a este taller.')
        return redirect('workshop:orders_list')
    
    # Obtener tareas y repuestos
    tasks = OrderService.get_order_tasks(order_id)
    
    # Para cada tarea, obtener sus repuestos
    for task in tasks:
        task['parts'] = OrderService.get_task_parts(task['id'])
    
    context = {
        'page_title': f'Orden #{order_id}',
        'active_page': 'orders',
        'order': order,
        'tasks': tasks,
        'task_types': VehicleService.get_task_types(),
        'inventory': InventoryService.get_all_inventory(workshop_id),
        'order_statuses': VehicleService.get_order_statuses(),
        'mechanics': EmployeeService.get_mechanics(workshop_id)
    }
    
    return render(request, 'workshop/order_detail.html', context)


@require_http_methods(["POST"])
@require_workshop_user
def order_update(request, order_id):
    """Actualiza información general de una orden."""
    workshop_id = request.workshop_id
    
    data = {}
    if request.POST.get('order_status_id'):
        data['order_status_id'] = int(request.POST.get('order_status_id'))
    if request.POST.get('assigned_mechanic_id'):
        data['assigned_mechanic_id'] = request.POST.get('assigned_mechanic_id')
    if request.POST.get('exit_date'):
        data['exit_date'] = request.POST.get('exit_date')
    if request.POST.get('observations'):
        data['observations'] = request.POST.get('observations')
    
    success = OrderService.update_order(order_id, workshop_id, data)
    
    if success:
        messages.success(request, '✅ Orden actualizada correctamente.')
    else:
        messages.error(request, '❌ Error al actualizar la orden.')
    
    return redirect('workshop:order_detail', order_id=order_id)


@require_http_methods(["POST"])
@require_workshop_user
def task_create(request, order_id):
    """Crea una nueva tarea en una orden."""
    workshop_id = request.workshop_id
    
    # Verificar que la orden pertenece al taller
    order = OrderService.get_order(order_id, workshop_id)
    if not order:
        messages.error(request, '❌ Orden no encontrada.')
        return redirect('workshop:orders_list')
    
    form = MaintenanceTaskForm(request.POST)
    if form.is_valid():
        task_data = {
            'task_type_id': form.cleaned_data['task_type_id'],
            'description': form.cleaned_data.get('description', ''),
            'cost': form.cleaned_data.get('cost', 0)
        }
        
        task = OrderService.create_task(order_id, task_data)
        
        if task:
            messages.success(request, '✅ Tarea agregada correctamente.')
        else:
            messages.error(request, '❌ Error al agregar la tarea.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:order_detail', order_id=order_id)


@require_http_methods(["POST"])
@require_workshop_user
def task_delete(request, order_id, task_id):
    """Elimina una tarea de una orden."""
    workshop_id = request.workshop_id
    
    # Verificar que la orden pertenece al taller
    order = OrderService.get_order(order_id, workshop_id)
    if not order:
        messages.error(request, '❌ Orden no encontrada.')
        return redirect('workshop:orders_list')
    
    success = OrderService.delete_task(task_id)
    
    if success:
        messages.success(request, '🗑️ Tarea eliminada.')
    else:
        messages.error(request, '❌ Error al eliminar la tarea.')
    
    return redirect('workshop:order_detail', order_id=order_id)


@require_http_methods(["POST"])
@require_workshop_user
def part_add_to_task(request, order_id):
    """Agrega un repuesto a una tarea."""
    workshop_id = request.workshop_id
    
    # Verificar que la orden pertenece al taller
    order = OrderService.get_order(order_id, workshop_id)
    if not order:
        messages.error(request, '❌ Orden no encontrada.')
        return redirect('workshop:orders_list')
    
    task_id = int(request.POST.get('maintenance_task_id'))
    inventory_id = int(request.POST.get('workshop_inventory_id'))
    quantity = int(request.POST.get('quantity_used'))
    
    part = OrderService.add_part_to_task(task_id, inventory_id, quantity)
    
    if part:
        messages.success(request, '✅ Repuesto agregado y stock actualizado.')
    else:
        messages.error(request, '❌ Error al agregar repuesto (verifica stock disponible).')
    
    return redirect('workshop:order_detail', order_id=order_id)


@require_http_methods(["POST"])
@require_workshop_user
def part_remove_from_task(request, order_id, part_id):
    """Elimina un repuesto de una tarea y devuelve el stock."""
    workshop_id = request.workshop_id
    
    # Verificar que la orden pertenece al taller
    order = OrderService.get_order(order_id, workshop_id)
    if not order:
        messages.error(request, '❌ Orden no encontrada.')
        return redirect('workshop:orders_list')
    
    success = OrderService.delete_part_from_task(part_id)
    
    if success:
        messages.success(request, '🗑️ Repuesto eliminado y stock devuelto.')
    else:
        messages.error(request, '❌ Error al eliminar el repuesto.')
    
    return redirect('workshop:order_detail', order_id=order_id)


# ===== GESTIÓN DE INVENTARIO =====

@require_workshop_user
def inventory_list(request):
    """Lista del inventario del taller."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    
    context = {
        'page_title': 'Inventario del Taller',
        'active_page': 'inventory',
        'inventory': InventoryService.get_all_inventory(workshop_id),
        'spare_parts': InventoryService.search_spare_parts(),
        'suppliers': SupplierService.get_all_suppliers(workshop_id)
    }
    
    return render(request, 'workshop/inventory_list.html', context)


@require_http_methods(["POST"])
@require_workshop_user
def inventory_add(request):
    """Agrega un repuesto al inventario del taller."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    
    form = InventoryAddForm(request.POST)
    if form.is_valid():
        data = {
            'spare_part_id': form.cleaned_data['spare_part_id'],
            'quantity': form.cleaned_data['quantity'],
            'current_cost': form.cleaned_data['current_cost'],
            'supplier_id': form.cleaned_data.get('supplier_id'),
            'location': form.cleaned_data.get('location'),
            'workshop_sku': form.cleaned_data.get('workshop_sku')
        }
        
        item = InventoryService.add_to_inventory(workshop_id, user_id, data)
        
        if item:
            messages.success(request, '✅ Repuesto agregado al inventario.')
        else:
            messages.error(request, '❌ Error al agregar el repuesto.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:inventory_list')


@require_http_methods(["POST"])
@require_workshop_user
def inventory_update(request, inventory_id):
    """Actualiza stock o costo de un repuesto."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    
    form = InventoryUpdateForm(request.POST)
    if form.is_valid():
        data = {
            'quantity': form.cleaned_data['quantity'],
            'current_cost': form.cleaned_data['current_cost'],
            'supplier_id': form.cleaned_data.get('supplier_id'),
            'location': form.cleaned_data.get('location')
        }
        
        success = InventoryService.update_inventory(inventory_id, workshop_id, user_id, data)
        
        if success:
            messages.success(request, '✅ Inventario actualizado.')
        else:
            messages.error(request, '❌ Error al actualizar.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:inventory_list')


@require_http_methods(["POST"])
@require_workshop_user
def inventory_delete(request, inventory_id):
    """Elimina un repuesto del inventario."""
    workshop_id = request.workshop_id
    
    success = InventoryService.delete_from_inventory(inventory_id, workshop_id)
    
    if success:
        messages.success(request, '🗑️ Repuesto eliminado del inventario.')
    else:
        messages.error(request, '❌ Error al eliminar.')
    
    return redirect('workshop:inventory_list')


# ===== GESTIÓN DE PROVEEDORES =====

@require_workshop_user
def suppliers_list(request):
    """Lista de proveedores (globales + locales del taller)."""
    workshop_id = request.workshop_id
    
    context = {
        'page_title': 'Proveedores',
        'active_page': 'suppliers',
        'suppliers': SupplierService.get_all_suppliers(workshop_id)
    }
    
    return render(request, 'workshop/suppliers_list.html', context)


@require_http_methods(["POST"])
@require_workshop_user
def supplier_create(request):
    """Crea un nuevo proveedor local del taller."""
    workshop_id = request.workshop_id
    
    form = SupplierForm(request.POST)
    if form.is_valid():
        data = {
            'name': form.cleaned_data['name'],
            'rut': form.cleaned_data.get('rut'),
            'address': form.cleaned_data.get('address'),
            'phone': form.cleaned_data.get('phone'),
            'email': form.cleaned_data.get('email')
        }
        
        supplier = SupplierService.create_supplier(workshop_id, data)
        
        if supplier:
            messages.success(request, f'✅ Proveedor "{data["name"]}" creado correctamente.')
        else:
            messages.error(request, '❌ Error al crear el proveedor.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:suppliers_list')


@require_http_methods(["POST"])
@require_workshop_user
def supplier_update(request, supplier_id):
    """Actualiza un proveedor local del taller."""
    workshop_id = request.workshop_id
    
    form = SupplierForm(request.POST)
    if form.is_valid():
        data = {
            'name': form.cleaned_data['name'],
            'rut': form.cleaned_data.get('rut'),
            'address': form.cleaned_data.get('address'),
            'phone': form.cleaned_data.get('phone'),
            'email': form.cleaned_data.get('email')
        }
        
        success = SupplierService.update_supplier(supplier_id, workshop_id, data)
        
        if success:
            messages.success(request, '✅ Proveedor actualizado.')
        else:
            messages.error(request, '❌ Error al actualizar (solo puedes editar proveedores locales).')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:suppliers_list')


@require_http_methods(["POST"])
@require_workshop_user
def supplier_delete(request, supplier_id):
    """Elimina un proveedor local del taller."""
    workshop_id = request.workshop_id
    
    success = SupplierService.delete_supplier(supplier_id, workshop_id)
    
    if success:
        messages.success(request, '🗑️ Proveedor eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar (solo puedes eliminar proveedores locales).')
    
    return redirect('workshop:suppliers_list')


# ===== GESTIÓN DE EMPLEADOS (Solo Admin Taller) =====

@require_workshop_user
@require_admin_taller
def employees_list(request):
    """Lista de empleados del taller (solo Admin Taller)."""
    workshop_id = request.workshop_id
    
    context = {
        'page_title': 'Empleados del Taller',
        'active_page': 'employees',
        'employees': EmployeeService.get_all_employees(workshop_id),
        'roles': EmployeeService.get_available_roles()
    }
    
    return render(request, 'workshop/employees_list.html', context)


@require_http_methods(["POST"])
@require_workshop_user
@require_admin_taller
def employee_update(request, user_id):
    """Actualiza un empleado del taller (solo Admin Taller)."""
    workshop_id = request.workshop_id
    
    form = EmployeeForm(request.POST)
    if form.is_valid():
        data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'rut': form.cleaned_data.get('rut'),
            'phone': form.cleaned_data.get('phone'),
            'role_id': form.cleaned_data['role_id'],
            'is_active': form.cleaned_data.get('is_active', True)
        }
        
        success = EmployeeService.update_employee(user_id, workshop_id, data)
        
        if success:
            messages.success(request, '✅ Empleado actualizado.')
        else:
            messages.error(request, '❌ Error al actualizar.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('workshop:employees_list')


@require_http_methods(["POST"])
@require_workshop_user
@require_admin_taller
def employee_deactivate(request, user_id):
    """Desactiva un empleado (solo Admin Taller)."""
    workshop_id = request.workshop_id
    
    success = EmployeeService.deactivate_employee(user_id, workshop_id)
    
    if success:
        messages.success(request, '🚫 Empleado desactivado.')
    else:
        messages.error(request, '❌ Error al desactivar.')
    
    return redirect('workshop:employees_list')


@require_http_methods(["POST"])
@require_workshop_user
@require_admin_taller
def employee_activate(request, user_id):
    """Activa un empleado (solo Admin Taller)."""
    workshop_id = request.workshop_id
    
    success = EmployeeService.activate_employee(user_id, workshop_id)
    
    if success:
        messages.success(request, '✅ Empleado activado.')
    else:
        messages.error(request, '❌ Error al activar.')
    
    return redirect('workshop:employees_list')
