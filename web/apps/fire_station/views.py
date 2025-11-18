import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accounts.decorators import require_supabase_login

from .decorators import require_fire_station_user, require_jefe_cuartel
from .services.dashboard_service import DashboardService
from .services.vehicle_service import VehicleService
from .services.user_service import UserService
from .services.request_service import RequestService
from .forms import VehicleCreateForm, VehicleEditForm, UserProfileForm, UserCreateForm

logger = logging.getLogger('apps.fire_station')


def handle_form_errors(request, form, is_ajax, *, message='⚠️ Corrige los errores del formulario.'):
    """
    Maneja los errores de formularios de manera consistente para peticiones normales y AJAX.
    """
    if is_ajax:
        return JsonResponse({'success': False, 'errors': form.errors})
    messages.error(request, message)
    return None


# ===== DASHBOARD =====

@require_supabase_login
@require_fire_station_user
def dashboard(request):
    """Vista principal del panel del cuartel."""
    fire_station_id = request.fire_station_id
    fire_station_name = request.session.get('fire_station_name', 'Cuartel')
    
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard',
        'fire_station_name': fire_station_name
    }
    
    # Obtener estadísticas
    stats = DashboardService.get_statistics(fire_station_id)
    context.update(stats)
    
    # Obtener vehículos recientes
    context['recent_vehicles'] = DashboardService.get_recent_vehicles(fire_station_id, limit=5)
    
    # Obtener vehículos por tipo
    context['vehicles_by_type'] = DashboardService.get_vehicles_by_type(fire_station_id)
    
    return render(request, 'fire_station/dashboard.html', context)


# ===== GESTIÓN DE VEHÍCULOS =====

@require_supabase_login
@require_fire_station_user
def vehicles_list(request):
    """Lista de vehículos del cuartel."""
    fire_station_id = request.fire_station_id
    
    # Obtener filtros
    filters = {}
    if request.GET.get('status_id'):
        filters['status_id'] = request.GET.get('status_id')
    if request.GET.get('vehicle_type_id'):
        filters['vehicle_type_id'] = request.GET.get('vehicle_type_id')
    if request.GET.get('license_plate'):
        filters['license_plate'] = request.GET.get('license_plate')
    
    context = {
        'page_title': 'Gestión de Vehículos',
        'active_page': 'vehicles',
        'vehicles': VehicleService.get_all_vehicles(fire_station_id, filters),
        'vehicle_types': VehicleService.get_vehicle_types(),
        'vehicle_statuses': VehicleService.get_vehicle_statuses(),
        'fuel_types': VehicleService.get_fuel_types(),
        'transmission_types': VehicleService.get_transmission_types(),
        'oil_types': VehicleService.get_oil_types(),
        'coolant_types': VehicleService.get_coolant_types(),
        'filters': filters
    }
    
    return render(request, 'fire_station/vehicles_list.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def vehicle_create(request):
    """Crea un nuevo vehículo."""
    fire_station_id = request.fire_station_id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = VehicleCreateForm(request.POST)
    
    if form.is_valid():
        data = {
            'license_plate': form.cleaned_data['license_plate'],
            'brand': form.cleaned_data['brand'],
            'model': form.cleaned_data['model'],
            'year': form.cleaned_data['year'],
            'vehicle_type_id': form.cleaned_data['vehicle_type_id'],
            'vehicle_status_id': form.cleaned_data['vehicle_status_id'],
            'fire_station_id': fire_station_id,
            'engine_number': form.cleaned_data.get('engine_number'),
            'vin': form.cleaned_data.get('vin'),
            'mileage': form.cleaned_data.get('mileage'),
            'oil_capacity_liters': form.cleaned_data.get('oil_capacity_liters'),
            'registration_date': form.cleaned_data.get('registration_date'),
            'next_revision_date': form.cleaned_data.get('next_revision_date'),
            'fuel_type_id': form.cleaned_data.get('fuel_type_id'),
            'transmission_type_id': form.cleaned_data.get('transmission_type_id'),
            'oil_type_id': form.cleaned_data.get('oil_type_id'),
            'coolant_type_id': form.cleaned_data.get('coolant_type_id'),
        }
        
        # Convertir fechas a string ISO
        if data.get('registration_date'):
            data['registration_date'] = data['registration_date'].isoformat()
        if data.get('next_revision_date'):
            data['next_revision_date'] = data['next_revision_date'].isoformat()
        
        vehicle, errors = VehicleService.create_vehicle(data)
        
        if vehicle:
            message = f'✅ Vehículo "{data["license_plate"]}" creado correctamente.'
            if is_ajax:
                messages.success(request, message)
                return JsonResponse({'success': True, 'reload_page': True})
            messages.success(request, message)
            return redirect('fire_station:vehicles_list')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors or {'general': ['Error al crear el vehículo.']}})
            # Mostrar el primer error encontrado
            if errors:
                first_error = list(errors.values())[0]
                if isinstance(first_error, list) and first_error:
                    messages.error(request, f'❌ {first_error[0]}')
                else:
                    messages.error(request, '❌ Error al crear el vehículo.')
            else:
                messages.error(request, '❌ Error al crear el vehículo.')
    else:
        response = handle_form_errors(
            request,
            form,
            is_ajax,
            message='⚠️ Corrige los errores del formulario para crear el vehículo.'
        )
        if response:
            return response
    
    return redirect('fire_station:vehicles_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def vehicle_edit(request, vehicle_id):
    """Edita un vehículo existente."""
    fire_station_id = request.fire_station_id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Verificar que el vehículo existe y pertenece al cuartel
    vehicle = VehicleService.get_vehicle(vehicle_id, fire_station_id)
    if not vehicle:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Vehículo no encontrado.'})
        messages.error(request, '❌ Vehículo no encontrado.')
        return redirect('fire_station:vehicles_list')
    
    form = VehicleEditForm(request.POST)
    
    if form.is_valid():
        data = {
            'brand': form.cleaned_data['brand'],
            'model': form.cleaned_data['model'],
            'year': form.cleaned_data['year'],
            'vehicle_type_id': form.cleaned_data['vehicle_type_id'],
            'vehicle_status_id': form.cleaned_data['vehicle_status_id'],
            'mileage': form.cleaned_data.get('mileage'),
            'oil_capacity_liters': form.cleaned_data.get('oil_capacity_liters'),
            'registration_date': form.cleaned_data.get('registration_date'),
            'next_revision_date': form.cleaned_data.get('next_revision_date'),
            'fuel_type_id': form.cleaned_data.get('fuel_type_id'),
            'transmission_type_id': form.cleaned_data.get('transmission_type_id'),
            'oil_type_id': form.cleaned_data.get('oil_type_id'),
            'coolant_type_id': form.cleaned_data.get('coolant_type_id'),
        }
        
        # Convertir fechas a string ISO
        if data.get('registration_date'):
            data['registration_date'] = data['registration_date'].isoformat()
        if data.get('next_revision_date'):
            data['next_revision_date'] = data['next_revision_date'].isoformat()
        
        # Actualizar fecha de último kilometraje si cambió
        if data.get('mileage') and data['mileage'] != vehicle.get('mileage'):
            from datetime import datetime
            data['mileage_last_updated'] = datetime.utcnow().date().isoformat()
        
        success, errors = VehicleService.update_vehicle(vehicle_id, fire_station_id, data)
        
        if success:
            message = '✅ Vehículo actualizado correctamente.'
            if is_ajax:
                messages.success(request, message)
                return JsonResponse({'success': True, 'reload_page': True})
            messages.success(request, message)
            return redirect('fire_station:vehicles_list')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors or {'general': ['Error al actualizar el vehículo.']}})
            # Mostrar el primer error encontrado
            if errors:
                first_error = list(errors.values())[0]
                if isinstance(first_error, list) and first_error:
                    messages.error(request, f'❌ {first_error[0]}')
                else:
                    messages.error(request, '❌ Error al actualizar el vehículo.')
            else:
                messages.error(request, '❌ Error al actualizar el vehículo.')
    else:
        response = handle_form_errors(
            request,
            form,
            is_ajax,
            message='⚠️ Corrige los errores del formulario para actualizar el vehículo.'
        )
        if response:
            return response
    
    return redirect('fire_station:vehicles_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def vehicle_delete(request, vehicle_id):
    """Elimina un vehículo."""
    fire_station_id = request.fire_station_id
    
    success = VehicleService.delete_vehicle(vehicle_id, fire_station_id)
    
    if success:
        messages.success(request, '🗑️ Vehículo eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el vehículo (puede tener datos asociados).')
    
    return redirect('fire_station:vehicles_list')


# ===== GESTIÓN DE USUARIOS =====

@require_supabase_login
@require_fire_station_user
def users_list(request):
    """Lista de usuarios del cuartel (solo Jefe Cuartel)."""
    fire_station_id = request.fire_station_id
    
    context = {
        'page_title': 'Gestión de Usuarios',
        'active_page': 'users',
        'users': UserService.get_all_users(fire_station_id),
        'roles': UserService.get_fire_station_roles()
    }
    
    return render(request, 'fire_station/users_list.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def user_create(request):
    """Crea un nuevo usuario del cuartel."""
    fire_station_id = request.fire_station_id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Solo permitir crear usuarios con rol "Jefe Cuartel"
    all_roles = UserService.get_fire_station_roles()
    jefe_cuartel_roles = [role for role in all_roles if role.get('name') == 'Jefe Cuartel']
    
    if not jefe_cuartel_roles:
        error_msg = 'No se encontró el rol "Jefe Cuartel". Contacta al administrador.'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': {'general': [error_msg]}
            }, status=400)
        messages.error(request, f'❌ {error_msg}')
        return redirect('fire_station:users_list')
    
    role_choices = [(str(role['id']), role['name']) for role in jefe_cuartel_roles]
    
    form = UserCreateForm(request.POST, role_choices=role_choices)
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        # Validar que el rol es "Jefe Cuartel"
        role_id = cleaned_data['role_id']
        jefe_cuartel_role_ids = [role['id'] for role in jefe_cuartel_roles]
        
        if role_id not in jefe_cuartel_role_ids:
            error_msg = 'Solo se pueden crear usuarios con el rol "Jefe Cuartel".'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'role_id': [error_msg]}
                }, status=400)
            messages.error(request, f'❌ {error_msg}')
            return redirect('fire_station:users_list')
        
        # Crear el usuario
        result = UserService.create_user(
            email=cleaned_data['email'],
            password=cleaned_data['password'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            role_id=role_id,
            fire_station_id=fire_station_id,
            rut=cleaned_data.get('rut'),
            phone=cleaned_data.get('phone')
        )
        
        if result['success']:
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Usuario creado correctamente.',
                    'reload_page': True
                })
            messages.success(request, '✅ Usuario creado correctamente.')
            return redirect('fire_station:users_list')
        
        error_msg = result.get('error', 'Error al crear el usuario.')
        error_field = result.get('error_field')
        
        if is_ajax:
            if error_field and error_field != 'general':
                return JsonResponse({
                    'success': False,
                    'errors': {error_field: [error_msg]}
                }, status=400)
            else:
                return JsonResponse({
                    'success': False,
                    'errors': {'general': [error_msg]}
                }, status=400)
        messages.error(request, f'❌ {error_msg}')
        return redirect('fire_station:users_list')
    
    # Formulario inválido
    logger.warning(f"⚠️ Formulario inválido al crear usuario. Errores: {form.errors}")
    logger.warning(f"⚠️ Datos recibidos: {request.POST.dict()}")
    
    if is_ajax:
        # Formatear errores para que sean más legibles
        formatted_errors = {}
        for field, errors in form.errors.items():
            if isinstance(errors, list):
                formatted_errors[field] = errors
            else:
                formatted_errors[field] = [str(errors)]
        
        return JsonResponse({
            'success': False,
            'errors': formatted_errors
        }, status=400)
    messages.error(request, '❌ Datos inválidos. Verifica los campos del formulario.')
    return redirect('fire_station:users_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def user_edit(request, user_id):
    """Edita un usuario del cuartel."""
    fire_station_id = request.fire_station_id
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Verificar que el usuario existe y pertenece al cuartel
    user = UserService.get_user(user_id, fire_station_id)
    if not user:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})
        messages.error(request, '❌ Usuario no encontrado.')
        return redirect('fire_station:users_list')
    
    # Solo permitir editar usuarios con rol "Jefe Cuartel"
    all_roles = UserService.get_fire_station_roles()
    jefe_cuartel_roles = [role for role in all_roles if role.get('name') == 'Jefe Cuartel']
    
    if not jefe_cuartel_roles:
        error_msg = 'No se encontró el rol "Jefe Cuartel". Contacta al administrador.'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': {'general': [error_msg]}
            }, status=400)
        messages.error(request, f'❌ {error_msg}')
        return redirect('fire_station:users_list')
    
    role_choices = [(str(role['id']), role['name']) for role in jefe_cuartel_roles]
    
    form = UserProfileForm(request.POST, role_choices=role_choices)
    
    if form.is_valid():
        data = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'rut': form.cleaned_data.get('rut'),
            'phone': form.cleaned_data.get('phone'),
            'role_id': form.cleaned_data['role_id'],
            'is_active': form.cleaned_data.get('is_active', True),
        }
        
        # Validar que el rol es "Jefe Cuartel"
        role_id = form.cleaned_data['role_id']
        jefe_cuartel_role_ids = [role['id'] for role in jefe_cuartel_roles]
        
        if role_id not in jefe_cuartel_role_ids:
            error_msg = 'Solo se pueden editar usuarios con el rol "Jefe Cuartel".'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'role_id': [error_msg]}
                }, status=400)
            messages.error(request, f'❌ {error_msg}')
            return redirect('fire_station:users_list')
        
        success, errors = UserService.update_user(user_id, fire_station_id, data)
        
        if success:
            message = '✅ Usuario actualizado correctamente.'
            if is_ajax:
                messages.success(request, message)
                return JsonResponse({'success': True, 'reload_page': True})
            messages.success(request, message)
            return redirect('fire_station:users_list')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors or {'general': ['Error al actualizar el usuario.']}})
            # Para no-AJAX, mostrar el primer error
            first_error = list(errors.values())[0][0] if errors else 'Error al actualizar el usuario.'
            messages.error(request, f'❌ {first_error}')
    else:
        logger.warning(f"⚠️ Formulario inválido al editar usuario. Errores: {form.errors}")
        logger.warning(f"⚠️ Datos recibidos: {request.POST.dict()}")
        
        response = handle_form_errors(
            request,
            form,
            is_ajax,
            message='⚠️ Corrige los errores del formulario para actualizar el usuario.'
        )
        if response:
            return response
    
    return redirect('fire_station:users_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def user_deactivate(request, user_id):
    """Desactiva un usuario del cuartel."""
    fire_station_id = request.fire_station_id
    
    # Evitar que el jefe se desactive a sí mismo
    if request.session.get('sb_user_id') == user_id:
        messages.error(request, '❌ No puedes desactivar tu propia cuenta.')
        return redirect('fire_station:users_list')
    
    success = UserService.deactivate_user(user_id, fire_station_id)
    
    if success:
        messages.success(request, '🚫 Usuario desactivado.')
    else:
        messages.error(request, '❌ Error al desactivar el usuario.')
    
    return redirect('fire_station:users_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def user_activate(request, user_id):
    """Activa un usuario del cuartel."""
    fire_station_id = request.fire_station_id
    
    success = UserService.activate_user(user_id, fire_station_id)
    
    if success:
        messages.success(request, '✅ Usuario activado correctamente.')
    else:
        messages.error(request, '❌ Error al activar el usuario.')
    
    return redirect('fire_station:users_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def user_delete(request, user_id):
    """Elimina un usuario del cuartel."""
    fire_station_id = request.fire_station_id
    
    # Evitar que el jefe se elimine a sí mismo
    if request.session.get('sb_user_id') == user_id:
        messages.error(request, '❌ No puedes eliminar tu propia cuenta.')
        return redirect('fire_station:users_list')
    
    success = UserService.delete_user(user_id, fire_station_id)
    
    if success:
        messages.success(request, '🗑️ Usuario eliminado correctamente.')
    else:
        messages.error(request, '❌ Error al eliminar el usuario.')
    
    return redirect('fire_station:users_list')


# ===== API ENDPOINTS =====

@require_supabase_login
@require_fire_station_user
def api_get_vehicle(request, vehicle_id):
    """API endpoint para obtener los datos de un vehículo específico."""
    fire_station_id = request.fire_station_id
    
    vehicle = VehicleService.get_vehicle(vehicle_id, fire_station_id)
    
    if vehicle:
        # Formatear fechas
        if vehicle.get('registration_date'):
            vehicle['registration_date'] = str(vehicle['registration_date'])
        if vehicle.get('next_revision_date'):
            vehicle['next_revision_date'] = str(vehicle['next_revision_date'])
        if vehicle.get('mileage_last_updated'):
            vehicle['mileage_last_updated'] = str(vehicle['mileage_last_updated'])
        
        return JsonResponse({
            'success': True,
            'vehicle': vehicle
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Vehículo no encontrado'
        }, status=404)


@require_supabase_login
@require_fire_station_user
@require_jefe_cuartel
def api_get_user(request, user_id):
    """API endpoint para obtener los datos de un usuario específico."""
    fire_station_id = request.fire_station_id
    
    user = UserService.get_user(user_id, fire_station_id)
    
    if user:
        # Asegurar que role_id esté presente (puede venir en role.id)
        if 'role_id' not in user and 'role' in user:
            if isinstance(user['role'], dict) and 'id' in user['role']:
                user['role_id'] = user['role']['id']
        
        return JsonResponse({
            'success': True,
            'user': user
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=404)


# ===== HISTORIAL DE VEHÍCULOS =====

@require_supabase_login
@require_fire_station_user
def vehicle_history(request, vehicle_id):
    """Vista del historial de cambios de estado de un vehículo."""
    fire_station_id = request.fire_station_id
    
    vehicle = VehicleService.get_vehicle(vehicle_id, fire_station_id)
    if not vehicle:
        messages.error(request, '❌ Vehículo no encontrado.')
        return redirect('fire_station:vehicles_list')
    
    history = VehicleService.get_vehicle_status_history(vehicle_id, fire_station_id)
    
    context = {
        'page_title': f'Historial - {vehicle["license_plate"]}',
        'active_page': 'vehicles',
        'vehicle': vehicle,
        'history': history
    }
    
    return render(request, 'fire_station/vehicle_history.html', context)


# ===== SOLICITUDES DE MANTENIMIENTO =====

@require_supabase_login
@require_fire_station_user
def requests_list(request):
    """Lista de solicitudes de mantenimiento del cuartel."""
    fire_station_id = request.fire_station_id
    
    # Obtener filtros
    filters = {}
    if request.GET.get('status_id'):
        filters['status_id'] = request.GET.get('status_id')
    if request.GET.get('vehicle_id'):
        filters['vehicle_id'] = request.GET.get('vehicle_id')
    
    context = {
        'page_title': 'Solicitudes de Mantenimiento',
        'active_page': 'requests',
        'requests': RequestService.get_all_requests(fire_station_id, filters),
        'vehicles': VehicleService.get_all_vehicles(fire_station_id),
        'request_types': RequestService.get_request_types(),
        'request_statuses': RequestService.get_request_statuses(),
        'filters': filters
    }
    
    return render(request, 'fire_station/requests_list.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
def request_create(request):
    """Crea una nueva solicitud de mantenimiento."""
    fire_station_id = request.fire_station_id
    user_id = request.session.get('sb_user_id')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    vehicle_id = request.POST.get('vehicle_id')
    request_type_id = request.POST.get('request_type_id')
    description = request.POST.get('description', '').strip()
    
    # Validar campos requeridos
    if not vehicle_id or not request_type_id or not description:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'general': ['Todos los campos son requeridos.']}})
        messages.error(request, '❌ Todos los campos son requeridos.')
        return redirect('fire_station:requests_list')
    
    # Verificar que el vehículo pertenece al cuartel
    vehicle = VehicleService.get_vehicle(int(vehicle_id), fire_station_id)
    if not vehicle:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'general': ['Vehículo no encontrado.']}})
        messages.error(request, '❌ Vehículo no encontrado.')
        return redirect('fire_station:requests_list')
    
    data = {
        'vehicle_id': int(vehicle_id),
        'fire_station_id': fire_station_id,
        'requested_by_user_id': user_id,
        'request_type_id': int(request_type_id),
        'description': description
    }
    
    maintenance_request = RequestService.create_request(data)
    
    if maintenance_request:
        message = f'✅ Solicitud de mantenimiento creada correctamente.'
        if is_ajax:
            messages.success(request, message)
            return JsonResponse({'success': True, 'reload_page': True})
        messages.success(request, message)
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'general': ['Error al crear la solicitud.']}})
        messages.error(request, '❌ Error al crear la solicitud.')
    
    return redirect('fire_station:requests_list')


@require_supabase_login
@require_fire_station_user
def request_detail(request, request_id):
    """Vista de detalle de una solicitud de mantenimiento."""
    fire_station_id = request.fire_station_id
    
    maintenance_request = RequestService.get_request(request_id, fire_station_id)
    if not maintenance_request:
        messages.error(request, '❌ Solicitud no encontrada.')
        return redirect('fire_station:requests_list')
    
    context = {
        'page_title': f'Solicitud #{request_id}',
        'active_page': 'requests',
        'request': maintenance_request
    }
    
    return render(request, 'fire_station/request_detail.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_fire_station_user
def request_cancel(request, request_id):
    """Cancela una solicitud de mantenimiento."""
    fire_station_id = request.fire_station_id
    
    success = RequestService.cancel_request(request_id, fire_station_id)
    
    if success:
        messages.success(request, '❌ Solicitud cancelada.')
    else:
        messages.error(request, '❌ Error al cancelar la solicitud (puede que ya esté procesada).')
    
    return redirect('fire_station:requests_list')


@require_supabase_login
@require_fire_station_user
def api_get_request(request, request_id):
    """API endpoint para obtener los datos de una solicitud específica."""
    fire_station_id = request.fire_station_id
    
    maintenance_request = RequestService.get_request(request_id, fire_station_id)
    
    if maintenance_request:
        # Formatear fechas
        if maintenance_request.get('created_at'):
            maintenance_request['created_at'] = str(maintenance_request['created_at'])
        if maintenance_request.get('updated_at'):
            maintenance_request['updated_at'] = str(maintenance_request['updated_at'])
        
        return JsonResponse({
            'success': True,
            'request': maintenance_request
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)

