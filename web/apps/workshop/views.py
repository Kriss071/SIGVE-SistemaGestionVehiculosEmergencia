import logging
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from .decorators import require_workshop_user, require_admin_taller
from .services.dashboard_service import DashboardService
from .services.order_service import OrderService
from .services.inventory_service import InventoryService
from .services.supplier_service import SupplierService
from .services.employee_service import EmployeeService
from .services.vehicle_service import VehicleService
from .services.request_service import RequestService
from apps.sigve.services.workshop_service import WorkshopService
from .forms import (
    VehicleSearchForm, VehicleCreateForm, MaintenanceOrderForm,
    MaintenanceTaskForm, TaskPartForm, InventoryAddForm,
    InventoryUpdateForm, SupplierForm, EmployeeForm, EmployeeCreateForm,
    DataRequestForm
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
    
    # Obtener solicitudes pendientes
    context['pending_requests_count'] = RequestService.get_pending_requests_count(workshop_id)
    
    # Obtener IDs de estados de orden para los links del dashboard
    order_statuses = VehicleService.get_order_statuses()
    status_id_map = {status['name']: status['id'] for status in order_statuses}
    context['status_id_en_taller'] = status_id_map.get('En Taller')
    context['status_id_pendiente'] = status_id_map.get('Pendiente')
    context['status_id_espera_repuesto'] = status_id_map.get('En Espera de Repuestos')
    
    return render(request, 'workshop/dashboard.html', context)


# ===== GESTIÓN DE ÓRDENES DE MANTENCIÓN =====

@require_workshop_user
@require_GET
def order_create_context_api(request):
    """Devuelve datos de contexto para inicializar el modal de órdenes."""
    from .services.order_service import OrderService
    
    workshop_id = request.workshop_id
    
    maintenance_types = VehicleService.get_maintenance_types()
    all_order_statuses = VehicleService.get_order_statuses()
    
    # Filtrar estados de finalización (Cancelada, Terminada, etc.) para creación
    # Solo se permiten estados activos al crear una orden
    order_statuses = [
        status for status in all_order_statuses
        if not OrderService.is_completion_status(status.get('name', ''))
    ]
    
    fire_stations = VehicleService.get_all_fire_stations()
    vehicle_catalog_data = VehicleService.get_catalog_data()
    
    mechanics = EmployeeService.get_mechanics(workshop_id)
    mechanics_with_full_name = [
        {
            **mechanic,
            'full_name': f"{mechanic.get('first_name', '')} {mechanic.get('last_name', '')}".strip()
        }
        for mechanic in mechanics
    ]
    
    data = {
        'success': True,
        'maintenance_types': maintenance_types,
        'order_statuses': order_statuses,
        'mechanics': mechanics_with_full_name,
        'vehicle_catalog_data': vehicle_catalog_data,
        'fire_stations': fire_stations
    }
    
    return JsonResponse(data)


@require_workshop_user
@require_GET
def vehicle_search_api(request):
    """Busca vehículos por patente para el modal de órdenes."""
    query = request.GET.get('q', '').strip()
    vehicles = VehicleService.search_vehicles(query)
    vehicle_ids = [vehicle.get('id') for vehicle in vehicles]
    active_orders_map = OrderService.get_active_orders_for_vehicles(vehicle_ids)
    
    for vehicle in vehicles:
        status = (vehicle.get('vehicle_status') or {}).get('name')
        vehicle['vehicle_status_name'] = status
        vehicle_id = vehicle.get('id')
        if vehicle_id in active_orders_map:
            vehicle['has_active_order'] = True
            vehicle['active_order_status'] = active_orders_map[vehicle_id].get('status_name')
        else:
            vehicle['has_active_order'] = False
            vehicle['active_order_status'] = None
    
    return JsonResponse({
        'success': True,
        'vehicles': vehicles
    })


@require_workshop_user
@require_POST
def vehicle_create_api(request):
    """Crea un nuevo vehículo desde el modal de órdenes."""
    form = VehicleCreateForm(request.POST)
    
    if not form.is_valid():
        # Convertir errores de formulario a formato consistente
        errors = {}
        for field, field_errors in form.errors.items():
            if isinstance(field_errors, list):
                errors[field] = field_errors
            else:
                errors[field] = [str(field_errors)]
        
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)
    
    vehicle_data = form.cleaned_data.copy()
    
    # Convertir campos opcionales vacíos a None (VIN y engine_number ahora son obligatorios)
    optional_fields = ['fuel_type_id', 'transmission_type_id']
    for field in optional_fields:
        if field in vehicle_data and (vehicle_data[field] == '' or vehicle_data[field] is None):
            vehicle_data[field] = None
    
    # Asegurar que engine_number y vin no sean None (ya están validados en el formulario)
    if 'engine_number' in vehicle_data:
        vehicle_data['engine_number'] = vehicle_data['engine_number'].strip() if vehicle_data['engine_number'] else None
    if 'vin' in vehicle_data:
        vehicle_data['vin'] = vehicle_data['vin'].strip() if vehicle_data['vin'] else None
    
    vehicle, duplicate_errors = VehicleService.create_vehicle(vehicle_data)
    
    if duplicate_errors:
        # Convertir errores de duplicación a formato de arrays
        errors = {}
        for field, error_msg in duplicate_errors.items():
            errors[field] = [error_msg] if isinstance(error_msg, str) else error_msg
        
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)
    
    if not vehicle:
        return JsonResponse({
            'success': False,
            'errors': {
                'general': ['No se pudo crear el vehículo. Inténtalo nuevamente.']
            }
        }, status=500)
    
    # Obtener datos completos del vehículo recién creado (incluye estado)
    vehicle_full = VehicleService.search_vehicle(vehicle.get('license_plate'))
    if vehicle_full:
        vehicle_full['vehicle_status_name'] = (vehicle_full.get('vehicle_status') or {}).get('name')
        vehicle_full['has_active_order'] = False
        vehicle_full['active_order_status'] = None
        vehicle = vehicle_full
    else:
        vehicle['vehicle_status_name'] = None
        vehicle['has_active_order'] = False
        vehicle['active_order_status'] = None
    
    return JsonResponse({
        'success': True,
        'vehicle': vehicle
    })


@require_workshop_user
@require_POST
def order_create_api(request):
    """Crea una nueva orden de mantención desde el modal."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    form = MaintenanceOrderForm(request.POST)
    
    if not form.is_valid():
        # Convertir errores de formulario a formato consistente
        errors = {}
        for field, field_errors in form.errors.items():
            if isinstance(field_errors, list):
                errors[field] = field_errors
            else:
                errors[field] = [str(field_errors)]
        
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)
    
    cleaned = form.cleaned_data
    
    if OrderService.has_active_order(cleaned['vehicle_id']):
        return JsonResponse({
            'success': False,
            'errors': {
                'vehicle_id': ['El vehículo seleccionado ya cuenta con una orden activa en el taller.']
            }
        }, status=400)
    
    order_data = {
        'vehicle_id': cleaned['vehicle_id'],
        'mileage': cleaned['mileage'],
        'maintenance_type_id': cleaned['maintenance_type_id'],
        'order_status_id': cleaned['order_status_id'],
        'assigned_mechanic_id': cleaned.get('assigned_mechanic_id') or None,
        'entry_date': cleaned['entry_date'].isoformat(),
        'observations': cleaned.get('observations', '')
    }
    
    order = OrderService.create_order(workshop_id, order_data, user_id)
    
    if not order:
        return JsonResponse({
            'success': False,
            'error': 'No se pudo crear la orden de mantención. Inténtalo nuevamente.'
        }, status=500)
    
    return JsonResponse({
        'success': True,
        'order': order
    })


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
                user_id = request.session.get('sb_user_id')
                order_data = {
                    'vehicle_id': form.cleaned_data['vehicle_id'],
                    'mileage': form.cleaned_data['mileage'],
                    'maintenance_type_id': form.cleaned_data['maintenance_type_id'],
                    'order_status_id': form.cleaned_data['order_status_id'],
                    'assigned_mechanic_id': form.cleaned_data.get('assigned_mechanic_id') or None,
                    'entry_date': form.cleaned_data.get('entry_date', datetime.now().date()).isoformat(),
                    'observations': form.cleaned_data.get('observations', '')
                }
                
                if OrderService.has_active_order(order_data['vehicle_id']):
                    messages.error(request, '❌ El vehículo seleccionado ya cuenta con una orden activa en el taller.')
                    return redirect('workshop:order_create')
                
                order = OrderService.create_order(workshop_id, order_data, user_id)
                
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
    
    # Verificar si la orden está completada
    order['is_completed'] = OrderService.is_order_completed(order)
    
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
        'maintenance_types': VehicleService.get_maintenance_types(),
        'mechanics': EmployeeService.get_mechanics(workshop_id)
    }
    
    return render(request, 'workshop/order_detail.html', context)


@require_http_methods(["POST"])
@require_workshop_user
def order_update(request, order_id):
    """Actualiza información general de una orden."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    
    # Verificar que la orden existe y pertenece al taller
    order = OrderService.get_order(order_id, workshop_id)
    if not order:
        messages.error(request, '❌ Orden no encontrada.')
        return redirect('workshop:orders_list')
    
    # Verificar si la orden ya está completada
    if OrderService.is_order_completed(order):
        messages.error(request, '❌ No se puede modificar una orden que ya está terminada.')
        return redirect('workshop:order_detail', order_id=order_id)
    
    data = {}
    if request.POST.get('order_status_id'):
        data['order_status_id'] = int(request.POST.get('order_status_id'))
    if request.POST.get('maintenance_type_id'):
        data['maintenance_type_id'] = int(request.POST.get('maintenance_type_id'))
    if request.POST.get('assigned_mechanic_id'):
        data['assigned_mechanic_id'] = request.POST.get('assigned_mechanic_id')
    # Manejar exit_date: solo incluir si se envía (puede estar vacío)
    exit_date_value = request.POST.get('exit_date', '').strip()
    if exit_date_value:
        data['exit_date'] = exit_date_value
    # Si se envía vacío explícitamente y no hay order_status_id, no incluir en data
    # (para permitir actualizar solo observaciones sin afectar exit_date)
    
    if request.POST.get('observations') is not None:
        data['observations'] = request.POST.get('observations', '')
    
    # Validar que si se cambia a estado de finalización, se requiera fecha de salida
    if data.get('order_status_id'):
        order_statuses = VehicleService.get_order_statuses()
        selected_status = next((s for s in order_statuses if s['id'] == data['order_status_id']), None)
        if selected_status and OrderService.is_completion_status(selected_status.get('name', '')):
            if not data.get('exit_date'):
                messages.error(request, '❌ Para finalizar la orden, debe ingresar la fecha de salida.')
                return redirect('workshop:order_detail', order_id=order_id)
            
            # Validar que la fecha de salida no sea anterior a la fecha de ingreso
            from datetime import datetime
            try:
                exit_date = datetime.strptime(data['exit_date'], '%Y-%m-%d').date()
                entry_date = datetime.strptime(order['entry_date'], '%Y-%m-%d').date() if isinstance(order['entry_date'], str) else order['entry_date']
                if exit_date < entry_date:
                    messages.error(request, '❌ La fecha de salida no puede ser anterior a la fecha de ingreso.')
                    return redirect('workshop:order_detail', order_id=order_id)
            except (ValueError, KeyError) as e:
                logger.error(f"Error validando fechas: {e}")
                messages.error(request, '❌ Error al validar las fechas. Por favor, verifique los datos.')
                return redirect('workshop:order_detail', order_id=order_id)
    
    success = OrderService.update_order(order_id, workshop_id, data, user_id)
    
    if success:
        # Verificar si la orden fue marcada como terminada
        new_status_id = data.get('order_status_id')
        if new_status_id:
            order_statuses = VehicleService.get_order_statuses()
            selected_status = next((s for s in order_statuses if s['id'] == new_status_id), None)
            if selected_status and OrderService.is_completion_status(selected_status.get('name', '')):
                messages.success(request, '✅ Orden marcada como terminada. El vehículo ha sido marcado como Disponible.')
            else:
                messages.success(request, '✅ Orden actualizada correctamente.')
        else:
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
    
    # Verificar si la orden está completada
    if OrderService.is_order_completed(order):
        messages.error(request, '❌ No se pueden agregar tareas a una orden terminada.')
        return redirect('workshop:order_detail', order_id=order_id)
    
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
    
    # Verificar si la orden está completada
    if OrderService.is_order_completed(order):
        messages.error(request, '❌ No se pueden eliminar tareas de una orden terminada.')
        return redirect('workshop:order_detail', order_id=order_id)
    
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
    
    # Verificar si la orden está completada
    if OrderService.is_order_completed(order):
        messages.error(request, '❌ No se pueden agregar repuestos a una orden terminada.')
        return redirect('workshop:order_detail', order_id=order_id)
    
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
    
    # Verificar si la orden está completada
    if OrderService.is_order_completed(order):
        messages.error(request, '❌ No se pueden eliminar repuestos de una orden terminada.')
        return redirect('workshop:order_detail', order_id=order_id)
    
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
        'suppliers': SupplierService.get_all_suppliers(workshop_id),
        'request_types': RequestService.get_all_request_types()
    }
    
    return render(request, 'workshop/inventory_list.html', context)


@require_http_methods(["POST"])
@require_workshop_user
def inventory_add(request):
    """Agrega un repuesto al inventario del taller."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = InventoryAddForm(request.POST)
    if form.is_valid():
        data = {
            'spare_part_id': form.cleaned_data['spare_part_id'],
            'quantity': form.cleaned_data['quantity'],
            'current_cost': form.cleaned_data['current_cost'],
            'supplier_id': form.cleaned_data.get('supplier_id') or None,
            'location': form.cleaned_data.get('location') or None,
            'workshop_sku': form.cleaned_data.get('workshop_sku') or None
        }
        
        item, duplicate_errors = InventoryService.add_to_inventory(workshop_id, user_id, data)
        
        if item:
            messages.success(request, '✅ Repuesto agregado al inventario correctamente.')
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'reload_page': True
                })
            return redirect('workshop:inventory_list')
        else:
            # Si hay errores de duplicación, agregarlos al formulario
            if duplicate_errors:
                for field, error_msg in duplicate_errors.items():
                    if field == 'general':
                        form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                    else:
                        form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                
                # Manejar errores del formulario
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': form.errors})
                messages.error(request, '⚠️ Corrige los errores del formulario para agregar el repuesto.')
                logger.warning(f"Errores de duplicación al agregar inventario: {duplicate_errors}")
            else:
                # Error genérico
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al agregar el repuesto.']}})
                messages.error(request, '❌ Error al agregar el repuesto.')
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors})
        messages.error(request, '❌ Datos inválidos. Verifica los campos del formulario.')
        logger.warning(f"Errores en formulario de agregar inventario: {form.errors}")
    
    return redirect('workshop:inventory_list')


@require_http_methods(["GET"])
@require_workshop_user
def inventory_detail_api(request, inventory_id):
    """API para obtener los datos de un item del inventario."""
    workshop_id = request.workshop_id
    
    item = InventoryService.get_inventory_item(inventory_id, workshop_id)
    
    if not item:
        return JsonResponse({
            'success': False,
            'error': 'Item de inventario no encontrado.'
        }, status=404)
    
    return JsonResponse({
        'success': True,
        'item': item
    })


@require_http_methods(["POST"])
@require_workshop_user
def inventory_update(request, inventory_id):
    """Actualiza stock, costo y otros datos de un repuesto."""
    workshop_id = request.workshop_id
    user_id = request.session.get('sb_user_id')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = InventoryUpdateForm(request.POST)
    if form.is_valid():
        data = {
            'quantity': form.cleaned_data['quantity'],
            'current_cost': form.cleaned_data['current_cost'],
            'supplier_id': form.cleaned_data.get('supplier_id') or None,
            'location': form.cleaned_data.get('location') or None,
            'workshop_sku': form.cleaned_data.get('workshop_sku') or None
        }
        
        success, duplicate_errors = InventoryService.update_inventory(inventory_id, workshop_id, user_id, data)
        
        if success:
            messages.success(request, '✅ Inventario actualizado correctamente.')
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'reload_page': True
                })
            return redirect('workshop:inventory_list')
        else:
            # Si hay errores de duplicación, agregarlos al formulario
            if duplicate_errors:
                for field, error_msg in duplicate_errors.items():
                    if field == 'general':
                        form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                    else:
                        form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                
                # Manejar errores del formulario
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': form.errors})
                messages.error(request, '⚠️ Corrige los errores del formulario para actualizar el inventario.')
                logger.warning(f"Errores de duplicación al actualizar inventario: {duplicate_errors}")
            else:
                # Error genérico
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el inventario.']}})
                messages.error(request, '❌ Error al actualizar el inventario.')
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors})
        messages.error(request, '❌ Datos inválidos. Verifica los campos del formulario.')
        logger.warning(f"Errores en formulario de actualización de inventario: {form.errors}")
    
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


@require_http_methods(["GET"])
@require_workshop_user
def supplier_detail_api(request, supplier_id):
    """API para obtener los datos de un proveedor."""
    workshop_id = request.workshop_id
    
    supplier = SupplierService.get_supplier(supplier_id, workshop_id)
    
    if not supplier:
        return JsonResponse({
            'success': False,
            'error': 'Proveedor no encontrado.'
        }, status=404)
    
    # Agregar flag is_global si no está presente
    if 'is_global' not in supplier:
        supplier['is_global'] = supplier.get('workshop_id') is None
    
    return JsonResponse({
        'success': True,
        'supplier': supplier
    })


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


@require_http_methods(["POST"])
@require_workshop_user
@require_admin_taller
def employee_create(request):
    """Crea un nuevo empleado del taller (solo Admin Taller)."""
    workshop_id = request.workshop_id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = EmployeeCreateForm(request.POST)
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        # Validar que el rol es Admin Taller o Mecánico
        role_id = cleaned_data['role_id']
        available_roles = EmployeeService.get_available_roles()
        role_ids = [role['id'] for role in available_roles]
        
        if role_id not in role_ids:
            error_msg = 'Rol no válido. Solo se pueden crear Admin Taller o Mecánicos.'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'role_id': [error_msg]}
                }, status=400)
            messages.error(request, f'❌ {error_msg}')
            return redirect('workshop:employees_list')
        
        # Crear el empleado
        result = EmployeeService.create_employee(
            email=cleaned_data['email'],
            password=cleaned_data['password'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            role_id=role_id,
            workshop_id=workshop_id,
            rut=cleaned_data.get('rut'),
            phone=cleaned_data.get('phone')
        )
        
        if result['success']:
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Empleado creado correctamente.',
                    'reload_page': True
                })
            messages.success(request, '✅ Empleado creado correctamente.')
            return redirect('workshop:employees_list')
        
        error_msg = result.get('error', 'Error al crear el empleado.')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': {'general': [error_msg]}
            }, status=400)
        messages.error(request, f'❌ {error_msg}')
        return redirect('workshop:employees_list')
    
    # Formulario inválido
    if is_ajax:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    messages.error(request, '❌ Datos inválidos. Verifica los campos del formulario.')
    return redirect('workshop:employees_list')


@require_http_methods(["GET"])
@require_workshop_user
@require_admin_taller
def employee_detail_api(request, user_id):
    """API para obtener los datos de un empleado (solo Admin Taller)."""
    workshop_id = request.workshop_id
    
    employee = EmployeeService.get_employee(user_id, workshop_id)
    
    if not employee:
        return JsonResponse({
            'success': False,
            'error': 'Empleado no encontrado.'
        }, status=404)
    
    return JsonResponse({
        'success': True,
        'employee': employee
    })


# ===== GESTIÓN DE SOLICITUDES A SIGVE =====

@require_workshop_user
def requests_list(request):
    """Lista de solicitudes del taller a SIGVE."""
    workshop_id = request.workshop_id
    
    # Obtener filtros
    filters = {}
    if request.GET.get('status'):
        filters['status'] = request.GET.get('status')
    if request.GET.get('request_type_id'):
        filters['request_type_id'] = request.GET.get('request_type_id')
    
    context = {
        'page_title': 'Solicitudes a SIGVE',
        'active_page': 'requests',
        'requests': RequestService.get_all_requests(workshop_id, filters),
        'request_types': RequestService.get_all_request_types(),
        'filters': filters
    }
    
    return render(request, 'workshop/requests_list.html', context)


@require_http_methods(["GET"])
@require_workshop_user
def request_type_schema_api(request, request_type_id):
    """API para obtener el esquema de un tipo de solicitud."""
    try:
        request_type = RequestService.get_request_type(request_type_id)
        
        if not request_type:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de solicitud no encontrado'
            }, status=404)
        
        # Asegurarse de que form_schema sea un objeto, no un string
        # Supabase devuelve JSONB como dict de Python, pero Django lo serializa correctamente
        # Solo necesitamos asegurarnos de que esté presente
        if 'form_schema' in request_type and request_type['form_schema']:
            # Si viene como string, parsearlo
            if isinstance(request_type['form_schema'], str):
                import json
                try:
                    request_type['form_schema'] = json.loads(request_type['form_schema'])
                except json.JSONDecodeError as e:
                    logger.error(f"Error al parsear form_schema del request_type {request_type_id}: {e}")
                    return JsonResponse({
                        'success': False,
                        'error': 'El esquema del formulario no es válido'
                    }, status=400)
        
        return JsonResponse({
            'success': True,
            'request_type': request_type
        })
    except Exception as e:
        logger.error(f"Error en request_type_schema_api para request_type_id {request_type_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@require_workshop_user
def request_create(request):
    """Crea una nueva solicitud a SIGVE."""
    user_id = request.session.get('sb_user_id')
    
    # Obtener los datos del formulario
    request_type_id = request.POST.get('request_type_id')
    
    if not request_type_id:
        messages.error(request, '❌ Debe seleccionar un tipo de solicitud.')
        return redirect('workshop:requests_list')
    
    # Obtener el tipo de solicitud para validar los campos
    request_type = RequestService.get_request_type(int(request_type_id))
    
    if not request_type:
        messages.error(request, '❌ Tipo de solicitud no encontrado.')
        return redirect('workshop:requests_list')
    
    # Construir el diccionario de datos solicitados basándose en el form_schema
    requested_data = {}
    form_schema = request_type.get('form_schema', {})
    fields = form_schema.get('fields', [])
    
    for field in fields:
        field_name = field.get('name')
        field_value = request.POST.get(field_name)
        
        # Validar campos requeridos
        if field.get('required') and not field_value:
            messages.error(request, f'❌ El campo "{field.get("label", field_name)}" es requerido.')
            return redirect('workshop:requests_list')
        
        requested_data[field_name] = field_value
    
    # Crear la solicitud
    data = {
        'request_type_id': int(request_type_id),
        'requested_data': requested_data
    }
    
    new_request = RequestService.create_request(user_id, data)
    
    if new_request:
        messages.success(request, f'✅ Solicitud de "{request_type["name"]}" enviada correctamente.')
    else:
        messages.error(request, '❌ Error al crear la solicitud.')
    
    return redirect('workshop:requests_list')
