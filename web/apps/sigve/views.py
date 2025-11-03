import logging
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accounts.decorators import require_supabase_login, require_role

from .services.dashboard_service import DashboardService
from .services.request_service import RequestService
from .services.workshop_service import WorkshopService
from .services.fire_station_service import FireStationService
from .services.catalog_service import CatalogService
from .services.user_service import UserService
from .forms import (
    WorkshopForm, FireStationForm, SparePartForm, SupplierForm,
    CatalogItemForm, UserProfileForm, RejectRequestForm
)

logger = logging.getLogger(__name__)


# ===== DASHBOARD =====

@require_supabase_login
@require_role("Admin SIGVE")
def dashboard(request):
    """Vista principal del panel de administración SIGVE."""
    context = {
        'page_title': 'Dashboard SIGVE',
        'active_page': 'dashboard'
    }
    
    # Obtener estadísticas
    stats = DashboardService.get_statistics()
    context.update(stats)
    
    # Obtener actividad reciente
    context['recent_activity'] = DashboardService.get_recent_activity(limit=10)
    
    # Obtener solicitudes pendientes
    context['pending_requests_count'] = DashboardService.get_pending_requests_count()
    
    return render(request, 'sigve/dashboard.html', context)


# ===== CENTRO DE SOLICITUDES =====

@require_supabase_login
@require_role("Admin SIGVE")
def requests_center(request):
    """Centro de solicitudes con pestañas."""
    status = request.GET.get('status', 'pendiente')
    
    context = {
        'page_title': 'Centro de Solicitudes',
        'active_page': 'requests',
        'current_status': status,
        'requests': RequestService.get_requests_by_status(status)
    }
    
    return render(request, 'sigve/requests_center.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def approve_request(request, request_id):
    """Aprueba una solicitud."""
    admin_notes = request.POST.get('admin_notes', '')
    
    success = RequestService.approve_request(request_id, admin_notes)
    
    if success:
        messages.success(request, '✅ Solicitud aprobada correctamente.')
    else:
        messages.error(request, '❌ Error al aprobar la solicitud.')
    
    return redirect('sigve:requests_center')


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def reject_request(request, request_id):
    """Rechaza una solicitud."""
    form = RejectRequestForm(request.POST)
    
    if form.is_valid():
        admin_notes = form.cleaned_data['admin_notes']
        success = RequestService.reject_request(request_id, admin_notes)
        
        if success:
            messages.success(request, '🚫 Solicitud rechazada.')
        else:
            messages.error(request, '❌ Error al rechazar la solicitud.')
    else:
        messages.error(request, '❌ Datos inválidos.')
    
    return redirect('sigve:requests_center')


# ===== GESTIÓN DE TALLERES =====

@require_supabase_login
@require_role("Admin SIGVE")
def workshops_list(request):
    """Lista de talleres."""
    context = {
        'page_title': 'Gestión de Talleres',
        'active_page': 'workshops',
        'workshops': WorkshopService.get_all_workshops()
    }
    
    return render(request, 'sigve/workshops_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def workshop_create(request):
    """Crear un nuevo taller."""
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email')
            }
            
            workshop = WorkshopService.create_workshop(data)
            
            if workshop:
                messages.success(request, f'✅ Taller "{data["name"]}" creado correctamente.')
                return redirect('sigve:workshops_list')
            else:
                messages.error(request, '❌ Error al crear el taller.')
    else:
        form = WorkshopForm()
    
    context = {
        'page_title': 'Crear Taller',
        'active_page': 'workshops',
        'form': form
    }
    
    return render(request, 'sigve/workshop_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def workshop_edit(request, workshop_id):
    """Editar un taller existente."""
    workshop = WorkshopService.get_workshop(workshop_id)
    
    if not workshop:
        messages.error(request, '❌ Taller no encontrado.')
        return redirect('sigve:workshops_list')
    
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email')
            }
            
            success = WorkshopService.update_workshop(workshop_id, data)
            
            if success:
                messages.success(request, '✅ Taller actualizado correctamente.')
                return redirect('sigve:workshops_list')
            else:
                messages.error(request, '❌ Error al actualizar el taller.')
    else:
        form = WorkshopForm(initial=workshop)
    
    context = {
        'page_title': 'Editar Taller',
        'active_page': 'workshops',
        'form': form,
        'workshop': workshop
    }
    
    return render(request, 'sigve/workshop_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def workshop_delete(request, workshop_id):
    """Eliminar un taller."""
    success = WorkshopService.delete_workshop(workshop_id)
    
    if success:
        messages.success(request, '🗑️ Taller eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el taller (puede tener empleados o datos asociados).')
    
    return redirect('sigve:workshops_list')


# ===== GESTIÓN DE CUARTELES =====

@require_supabase_login
@require_role("Admin SIGVE")
def fire_stations_list(request):
    """Lista de cuarteles."""
    context = {
        'page_title': 'Gestión de Cuarteles',
        'active_page': 'fire_stations',
        'fire_stations': FireStationService.get_all_fire_stations()
    }
    
    return render(request, 'sigve/fire_stations_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def fire_station_create(request):
    """Crear un nuevo cuartel."""
    communes = FireStationService.get_all_communes()
    
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'commune_id': form.cleaned_data['commune_id']
            }
            
            fire_station = FireStationService.create_fire_station(data)
            
            if fire_station:
                messages.success(request, f'✅ Cuartel "{data["name"]}" creado correctamente.')
                return redirect('sigve:fire_stations_list')
            else:
                messages.error(request, '❌ Error al crear el cuartel.')
    else:
        form = FireStationForm()
    
    context = {
        'page_title': 'Crear Cuartel',
        'active_page': 'fire_stations',
        'form': form,
        'communes': communes
    }
    
    return render(request, 'sigve/fire_station_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def fire_station_edit(request, fire_station_id):
    """Editar un cuartel existente."""
    fire_station = FireStationService.get_fire_station(fire_station_id)
    communes = FireStationService.get_all_communes()
    
    if not fire_station:
        messages.error(request, '❌ Cuartel no encontrado.')
        return redirect('sigve:fire_stations_list')
    
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'commune_id': form.cleaned_data['commune_id']
            }
            
            success = FireStationService.update_fire_station(fire_station_id, data)
            
            if success:
                messages.success(request, '✅ Cuartel actualizado correctamente.')
                return redirect('sigve:fire_stations_list')
            else:
                messages.error(request, '❌ Error al actualizar el cuartel.')
    else:
        form = FireStationForm(initial=fire_station)
    
    context = {
        'page_title': 'Editar Cuartel',
        'active_page': 'fire_stations',
        'form': form,
        'fire_station': fire_station,
        'communes': communes
    }
    
    return render(request, 'sigve/fire_station_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def fire_station_delete(request, fire_station_id):
    """Eliminar un cuartel."""
    success = FireStationService.delete_fire_station(fire_station_id)
    
    if success:
        messages.success(request, '🗑️ Cuartel eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el cuartel (puede tener vehículos asociados).')
    
    return redirect('sigve:fire_stations_list')


# ===== GESTIÓN DE CATÁLOGOS MAESTROS =====

# Repuestos
@require_supabase_login
@require_role("Admin SIGVE")
def spare_parts_list(request):
    """Lista de repuestos maestros."""
    context = {
        'page_title': 'Catálogo de Repuestos',
        'active_page': 'spare_parts',
        'spare_parts': CatalogService.get_all_spare_parts()
    }
    
    return render(request, 'sigve/spare_parts_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def spare_part_create(request):
    """Crear un nuevo repuesto maestro."""
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'sku': form.cleaned_data['sku'],
                'brand': form.cleaned_data.get('brand'),
                'description': form.cleaned_data.get('description')
            }
            
            spare_part = CatalogService.create_spare_part(data)
            
            if spare_part:
                messages.success(request, f'✅ Repuesto "{data["name"]}" creado correctamente.')
                return redirect('sigve:spare_parts_list')
            else:
                messages.error(request, '❌ Error al crear el repuesto.')
    else:
        form = SparePartForm()
    
    context = {
        'page_title': 'Crear Repuesto',
        'active_page': 'spare_parts',
        'form': form
    }
    
    return render(request, 'sigve/spare_part_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def spare_part_edit(request, spare_part_id):
    """Editar un repuesto maestro."""
    spare_part = CatalogService.get_spare_part(spare_part_id)
    
    if not spare_part:
        messages.error(request, '❌ Repuesto no encontrado.')
        return redirect('sigve:spare_parts_list')
    
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'sku': form.cleaned_data['sku'],
                'brand': form.cleaned_data.get('brand'),
                'description': form.cleaned_data.get('description')
            }
            
            success = CatalogService.update_spare_part(spare_part_id, data)
            
            if success:
                messages.success(request, '✅ Repuesto actualizado correctamente.')
                return redirect('sigve:spare_parts_list')
            else:
                messages.error(request, '❌ Error al actualizar el repuesto.')
    else:
        form = SparePartForm(initial=spare_part)
    
    context = {
        'page_title': 'Editar Repuesto',
        'active_page': 'spare_parts',
        'form': form,
        'spare_part': spare_part
    }
    
    return render(request, 'sigve/spare_part_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def spare_part_delete(request, spare_part_id):
    """Eliminar un repuesto maestro."""
    success = CatalogService.delete_spare_part(spare_part_id)
    
    if success:
        messages.success(request, '🗑️ Repuesto eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el repuesto (puede estar en uso).')
    
    return redirect('sigve:spare_parts_list')


# Proveedores Globales
@require_supabase_login
@require_role("Admin SIGVE")
def suppliers_list(request):
    """Lista de proveedores globales."""
    context = {
        'page_title': 'Proveedores Globales',
        'active_page': 'suppliers',
        'suppliers': CatalogService.get_all_global_suppliers()
    }
    
    return render(request, 'sigve/suppliers_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def supplier_create(request):
    """Crear un nuevo proveedor global."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'rut': form.cleaned_data.get('rut'),
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email'),
                'workshop_id': None  # Proveedor global
            }
            
            supplier = CatalogService.create_supplier(data)
            
            if supplier:
                messages.success(request, f'✅ Proveedor "{data["name"]}" creado correctamente.')
                return redirect('sigve:suppliers_list')
            else:
                messages.error(request, '❌ Error al crear el proveedor.')
    else:
        form = SupplierForm()
    
    context = {
        'page_title': 'Crear Proveedor',
        'active_page': 'suppliers',
        'form': form
    }
    
    return render(request, 'sigve/supplier_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def supplier_edit(request, supplier_id):
    """Editar un proveedor."""
    supplier = CatalogService.get_supplier(supplier_id)
    
    if not supplier:
        messages.error(request, '❌ Proveedor no encontrado.')
        return redirect('sigve:suppliers_list')
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'rut': form.cleaned_data.get('rut'),
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email')
            }
            
            success = CatalogService.update_supplier(supplier_id, data)
            
            if success:
                messages.success(request, '✅ Proveedor actualizado correctamente.')
                return redirect('sigve:suppliers_list')
            else:
                messages.error(request, '❌ Error al actualizar el proveedor.')
    else:
        form = SupplierForm(initial=supplier)
    
    context = {
        'page_title': 'Editar Proveedor',
        'active_page': 'suppliers',
        'form': form,
        'supplier': supplier
    }
    
    return render(request, 'sigve/supplier_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def supplier_delete(request, supplier_id):
    """Eliminar un proveedor."""
    success = CatalogService.delete_supplier(supplier_id)
    
    if success:
        messages.success(request, '🗑️ Proveedor eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el proveedor.')
    
    return redirect('sigve:suppliers_list')


# Catálogos Genéricos (Lookup Tables)
CATALOG_CONFIG = {
    'vehicle_type': {'name': 'Tipos de Vehículo', 'singular': 'Tipo de Vehículo'},
    'vehicle_status': {'name': 'Estados de Vehículo', 'singular': 'Estado de Vehículo'},
    'fuel_type': {'name': 'Tipos de Combustible', 'singular': 'Tipo de Combustible'},
    'transmission_type': {'name': 'Tipos de Transmisión', 'singular': 'Tipo de Transmisión'},
    'oil_type': {'name': 'Tipos de Aceite', 'singular': 'Tipo de Aceite'},
    'coolant_type': {'name': 'Tipos de Refrigerante', 'singular': 'Tipo de Refrigerante'},
    'task_type': {'name': 'Tipos de Tarea', 'singular': 'Tipo de Tarea'},
    'role': {'name': 'Roles de Usuario', 'singular': 'Rol'},
}


@require_supabase_login
@require_role("Admin SIGVE")
def catalog_list(request, catalog_name):
    """Lista genérica de catálogo."""
    if catalog_name not in CATALOG_CONFIG:
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    config = CATALOG_CONFIG[catalog_name]
    
    context = {
        'page_title': config['name'],
        'active_page': 'catalogs',
        'catalog_name': catalog_name,
        'catalog_display_name': config['name'],
        'items': CatalogService.get_catalog_items(catalog_name)
    }
    
    return render(request, 'sigve/catalog_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def catalog_create(request, catalog_name):
    """Crear un item de catálogo."""
    if catalog_name not in CATALOG_CONFIG:
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    config = CATALOG_CONFIG[catalog_name]
    
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data.get('description')
            }
            
            item = CatalogService.create_catalog_item(catalog_name, data)
            
            if item:
                messages.success(request, f'✅ {config["singular"]} creado correctamente.')
                return redirect('sigve:catalog_list', catalog_name=catalog_name)
            else:
                messages.error(request, '❌ Error al crear el item.')
    else:
        form = CatalogItemForm()
    
    context = {
        'page_title': f'Crear {config["singular"]}',
        'active_page': 'catalogs',
        'catalog_name': catalog_name,
        'catalog_display_name': config['singular'],
        'form': form
    }
    
    return render(request, 'sigve/catalog_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def catalog_edit(request, catalog_name, item_id):
    """Editar un item de catálogo."""
    if catalog_name not in CATALOG_CONFIG:
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    config = CATALOG_CONFIG[catalog_name]
    item = CatalogService.get_catalog_item(catalog_name, item_id)
    
    if not item:
        messages.error(request, '❌ Item no encontrado.')
        return redirect('sigve:catalog_list', catalog_name=catalog_name)
    
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data.get('description')
            }
            
            success = CatalogService.update_catalog_item(catalog_name, item_id, data)
            
            if success:
                messages.success(request, '✅ Item actualizado correctamente.')
                return redirect('sigve:catalog_list', catalog_name=catalog_name)
            else:
                messages.error(request, '❌ Error al actualizar el item.')
    else:
        form = CatalogItemForm(initial=item)
    
    context = {
        'page_title': f'Editar {config["singular"]}',
        'active_page': 'catalogs',
        'catalog_name': catalog_name,
        'catalog_display_name': config['singular'],
        'form': form,
        'item': item
    }
    
    return render(request, 'sigve/catalog_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def catalog_delete(request, catalog_name, item_id):
    """Eliminar un item de catálogo."""
    if catalog_name not in CATALOG_CONFIG:
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    success = CatalogService.delete_catalog_item(catalog_name, item_id)
    
    if success:
        messages.success(request, '🗑️ Item eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el item (puede estar en uso).')
    
    return redirect('sigve:catalog_list', catalog_name=catalog_name)


# ===== GESTIÓN DE USUARIOS =====

@require_supabase_login
@require_role("Admin SIGVE")
def users_list(request):
    """Lista de todos los usuarios de la plataforma."""
    context = {
        'page_title': 'Gestión de Usuarios',
        'active_page': 'users',
        'users': UserService.get_all_users()
    }
    
    return render(request, 'sigve/users_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def user_edit(request, user_id):
    """Editar un usuario."""
    user = UserService.get_user(user_id)
    roles = UserService.get_all_roles()
    
    if not user:
        messages.error(request, '❌ Usuario no encontrado.')
        return redirect('sigve:users_list')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'rut': form.cleaned_data.get('rut'),
                'phone': form.cleaned_data.get('phone'),
                'role_id': form.cleaned_data['role_id'],
                'is_active': form.cleaned_data.get('is_active', True)
            }
            
            success = UserService.update_user(user_id, data)
            
            if success:
                messages.success(request, '✅ Usuario actualizado correctamente.')
                return redirect('sigve:users_list')
            else:
                messages.error(request, '❌ Error al actualizar el usuario.')
    else:
        form = UserProfileForm(initial=user)
    
    context = {
        'page_title': 'Editar Usuario',
        'active_page': 'users',
        'form': form,
        'user': user,
        'roles': roles
    }
    
    return render(request, 'sigve/user_form.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def user_deactivate(request, user_id):
    """Desactivar un usuario."""
    success = UserService.deactivate_user(user_id)
    
    if success:
        messages.success(request, '🚫 Usuario desactivado.')
    else:
        messages.error(request, '❌ Error al desactivar el usuario.')
    
    return redirect('sigve:users_list')
