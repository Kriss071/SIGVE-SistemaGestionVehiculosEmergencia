import logging
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accounts.decorators import require_supabase_login, require_role

from .services.dashboard_service import DashboardService
from .services.request_service import RequestService
from .services.request_type_service import RequestTypeService
from .services.workshop_service import WorkshopService
from .services.fire_station_service import FireStationService
from .services.catalog_service import CatalogService
from .services.user_service import UserService
from .forms import (
    WorkshopForm, FireStationForm, SparePartForm, SupplierForm,
    CatalogItemForm, UserProfileForm, RejectRequestForm, UserCreateForm,
    RequestTypeForm
)

logger = logging.getLogger('apps.workshop')


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
@require_role("Admin SIGVE")
def dashboard(request):
    """Vista principal del panel de administración SIGVE."""
    context = {
        'page_title': 'Dashboard',
        'active_page': 'dashboard'
    }
    
    # Obtener estadísticas
    stats = DashboardService.get_statistics()
    context.update(stats)
    
    # Obtener actividad reciente
    context['recent_activity'] = DashboardService.get_recent_activity(limit=10)
    
    # Obtener solicitudes pendientes
    context['pending_requests_count'] = DashboardService.get_pending_requests_count()
    
    # Contexto necesario para los modales
    context['communes'] = FireStationService.get_all_communes()
    
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
    logger.info("📥 Ingreso a la vista workshop_create - método: %s", request.method)

    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        logger.debug("Datos POST recibidos: %s", request.POST)
        logger.debug("Origen (source): %s | Es AJAX: %s", source, is_ajax)

        if form.is_valid():
            logger.info("✅ Formulario válido, preparando datos para creación de taller.")
            
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email'),
                'latitude': float(form.cleaned_data['latitude']) if form.cleaned_data.get('latitude') else None,
                'longitude': float(form.cleaned_data['longitude']) if form.cleaned_data.get('longitude') else None
            }
            
            logger.debug("Datos limpios del formulario: %s", data)

            workshop, duplicate_errors = WorkshopService.create_workshop(data)
            logger.info("Resultado de WorkshopService.create_workshop: workshop=%s, errors=%s", workshop, duplicate_errors)

            if workshop:
                message = f'✅ Taller "{data["name"]}" creado correctamente.'
                if is_ajax:
                    logger.debug("Petición AJAX — devolviendo JsonResponse de éxito.")
                    messages.success(request, message)
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                logger.info("Petición normal — redirigiendo a lista de talleres.")
                messages.success(request, message)
                return redirect('sigve:workshops_list')
            else:
                logger.error("❌ Error al crear taller en WorkshopService.")
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para crear el taller.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el taller.']}})
                    messages.error(request, '❌ Error al crear el taller.')
        else:
            logger.warning("⚠️ Formulario inválido: %s", form.errors)
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para crear el taller.'
            )
            if response:
                return response
    else:
        logger.info("📝 Petición GET — mostrando formulario vacío.")
        form = WorkshopForm()
    
    context = {
        'page_title': 'Crear Taller',
        'active_page': 'workshops',
        'form': form
    }

    logger.debug("Renderizando plantilla 'sigve/workshop_form.html' con contexto: %s", context.keys())
    return render(request, 'sigve/workshop_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def workshop_edit(request, workshop_id):
    """Editar un taller existente."""
    workshop = WorkshopService.get_workshop(workshop_id)
    
    if not workshop:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Taller no encontrado.'})
        messages.error(request, '❌ Taller no encontrado.')
        return redirect('sigve:workshops_list')
    
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        source = request.POST.get('source', 'list')  # 'dashboard' o 'list'
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            # El método clean() del formulario ya convierte cadenas vacías a None
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data.get('address'),
                'phone': form.cleaned_data.get('phone'),
                'email': form.cleaned_data.get('email'),
                'latitude': float(form.cleaned_data['latitude']) if form.cleaned_data.get('latitude') else None,
                'longitude': float(form.cleaned_data['longitude']) if form.cleaned_data.get('longitude') else None
            }
            
            success, duplicate_errors = WorkshopService.update_workshop(workshop_id, data)
            
            if success:
                # Si viene del dashboard y es AJAX, devolver JSON (sin redirección)
                if is_ajax:
                    messages.success(request, '✅ Taller actualizado correctamente.')
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                # Si viene de la lista o no es AJAX, redirigir normalmente
                messages.success(request, '✅ Taller actualizado correctamente.')
                return redirect('sigve:workshops_list')
            else:
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para actualizar el taller.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el taller.']}})
                    messages.error(request, '❌ Error al actualizar el taller.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para actualizar el taller.'
            )
            if response:
                return response
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
        'fire_stations': FireStationService.get_all_fire_stations(),
        'communes': FireStationService.get_all_communes()
    }
    
    return render(request, 'sigve/fire_stations_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def fire_station_create(request):
    """Crear un nuevo cuartel."""
    logger.info("📥 Ingreso a la vista fire_station_create - método: %s", request.method)
    communes = FireStationService.get_all_communes()
    
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        logger.debug("Datos POST recibidos: %s", request.POST)
        logger.debug("Origen (source): %s | Es AJAX: %s", source, is_ajax)
        
        if form.is_valid():
            logger.info("✅ Formulario válido, preparando datos para creación de cuartel.")
            
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'commune_id': form.cleaned_data['commune_id'],
                'latitude': float(form.cleaned_data['latitude']) if form.cleaned_data.get('latitude') else None,
                'longitude': float(form.cleaned_data['longitude']) if form.cleaned_data.get('longitude') else None
            }
            
            logger.debug("Datos limpios del formulario: %s", data)
            
            fire_station, duplicate_errors = FireStationService.create_fire_station(data)
            logger.info("Resultado de FireStationService.create_fire_station: fire_station=%s, errors=%s", fire_station, duplicate_errors)
            
            if fire_station:
                message = f'✅ Cuartel "{data["name"]}" creado correctamente.'
                if is_ajax:
                    logger.debug("Petición AJAX — devolviendo JsonResponse de éxito.")
                    messages.success(request, message)
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                logger.info("Petición normal — redirigiendo a lista de cuarteles.")
                messages.success(request, message)
                return redirect('sigve:fire_stations_list')
            else:
                logger.error("❌ Error al crear cuartel en FireStationService.")
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para crear el cuartel.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el cuartel.']}})
                    messages.error(request, '❌ Error al crear el cuartel.')
        else:
            logger.warning("⚠️ Formulario inválido: %s", form.errors)
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para crear el cuartel.'
            )
            if response:
                return response
    else:
        logger.info("📝 Petición GET — mostrando formulario vacío.")
        form = FireStationForm()
    
    context = {
        'page_title': 'Crear Cuartel',
        'active_page': 'fire_stations',
        'form': form,
        'communes': communes
    }
    
    logger.debug("Renderizando plantilla 'sigve/fire_station_form.html' con contexto: %s", context.keys())
    return render(request, 'sigve/fire_station_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def fire_station_edit(request, fire_station_id):
    """Editar un cuartel existente."""
    fire_station = FireStationService.get_fire_station(fire_station_id)
    communes = FireStationService.get_all_communes()
    
    if not fire_station:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Cuartel no encontrado.'})
        messages.error(request, '❌ Cuartel no encontrado.')
        return redirect('sigve:fire_stations_list')
    
    if request.method == 'POST':
        form = FireStationForm(request.POST)
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'commune_id': form.cleaned_data['commune_id'],
                'latitude': float(form.cleaned_data['latitude']) if form.cleaned_data.get('latitude') else None,
                'longitude': float(form.cleaned_data['longitude']) if form.cleaned_data.get('longitude') else None
            }
            
            success, duplicate_errors = FireStationService.update_fire_station(fire_station_id, data)
            
            if success:
                # Si viene del dashboard y es AJAX, devolver JSON (sin redirección)
                if is_ajax:
                    messages.success(request, '✅ Cuartel actualizado correctamente.')
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                # Si viene de la lista o no es AJAX, redirigir normalmente
                messages.success(request, '✅ Cuartel actualizado correctamente.')
                return redirect('sigve:fire_stations_list')
            else:
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para actualizar el cuartel.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el cuartel.']}})
                    messages.error(request, '❌ Error al actualizar el cuartel.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para actualizar el cuartel.'
            )
            if response:
                return response
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
    logger.info("📥 Ingreso a la vista spare_part_create - método: %s", request.method)
    
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        logger.debug("Datos POST recibidos: %s", request.POST)
        logger.debug("Origen (source): %s | Es AJAX: %s", source, is_ajax)
        
        if form.is_valid():
            logger.info("✅ Formulario válido, preparando datos para creación de repuesto.")
            
            data = {
                'name': form.cleaned_data['name'],
                'sku': form.cleaned_data['sku'],
                'brand': form.cleaned_data.get('brand'),
                'description': form.cleaned_data.get('description')
            }
            
            logger.debug("Datos limpios del formulario: %s", data)
            
            spare_part, duplicate_errors = CatalogService.create_spare_part(data)
            logger.info("Resultado de CatalogService.create_spare_part: spare_part=%s, errors=%s", spare_part, duplicate_errors)
            
            if spare_part:
                message = f'✅ Repuesto "{data["name"]}" creado correctamente.'
                if is_ajax:
                    logger.debug("Petición AJAX — devolviendo JsonResponse de éxito.")
                    messages.success(request, message)
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                logger.info("Petición normal — redirigiendo a lista de repuestos.")
                messages.success(request, message)
                return redirect('sigve:spare_parts_list')
            else:
                logger.error("❌ Error al crear repuesto en CatalogService.")
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para crear el repuesto.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el repuesto.']}})
                    messages.error(request, '❌ Error al crear el repuesto.')
        else:
            logger.warning("⚠️ Formulario inválido: %s", form.errors)
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para crear el repuesto.'
            )
            if response:
                return response
    else:
        logger.info("📝 Petición GET — mostrando formulario vacío.")
        form = SparePartForm()
    
    context = {
        'page_title': 'Crear Repuesto',
        'active_page': 'spare_parts',
        'form': form
    }
    
    logger.debug("Renderizando plantilla 'sigve/spare_part_form.html' con contexto: %s", context.keys())
    return render(request, 'sigve/spare_part_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def spare_part_edit(request, spare_part_id):
    """Editar un repuesto maestro."""
    spare_part = CatalogService.get_spare_part(spare_part_id)
    
    if not spare_part:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Repuesto no encontrado.'})
        messages.error(request, '❌ Repuesto no encontrado.')
        return redirect('sigve:spare_parts_list')
    
    if request.method == 'POST':
        form = SparePartForm(request.POST)
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'sku': form.cleaned_data['sku'],
                'brand': form.cleaned_data.get('brand'),
                'description': form.cleaned_data.get('description')
            }
            
            success, duplicate_errors = CatalogService.update_spare_part(spare_part_id, data)
            
            if success:
                # Si viene del dashboard y es AJAX, devolver JSON (sin redirección)
                if is_ajax:
                    messages.success(request, '✅ Repuesto actualizado correctamente.')
                    return JsonResponse({
                        'success': True,
                        'reload_page': True
                    })
                
                # Si viene de la lista o no es AJAX, redirigir normalmente
                messages.success(request, '✅ Repuesto actualizado correctamente.')
                return redirect('sigve:spare_parts_list')
            else:
                # Si hay errores de duplicación, agregarlos al formulario
                if duplicate_errors:
                    for field, error_msg in duplicate_errors.items():
                        if field == 'general':
                            # Si es un error general, agregarlo como error no asociado a un campo
                            form.add_error(None, error_msg if isinstance(error_msg, str) else error_msg[0])
                        else:
                            form.add_error(field, error_msg if isinstance(error_msg, str) else error_msg[0])
                    
                    # Manejar errores del formulario
                    response = handle_form_errors(
                        request,
                        form,
                        is_ajax,
                        message='⚠️ Corrige los errores del formulario para actualizar el repuesto.'
                    )
                    if response:
                        return response
                else:
                    # Error genérico
                    if is_ajax:
                        return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el repuesto.']}})
                    messages.error(request, '❌ Error al actualizar el repuesto.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para actualizar el repuesto.'
            )
            if response:
                return response
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
        source = request.POST.get('source', 'list')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
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
                message = f'✅ Proveedor "{data["name"]}" creado correctamente.'
                if is_ajax:
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'reload_page': True})
                
                messages.success(request, message)
                return redirect('sigve:suppliers_list')
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el proveedor.']}})
                messages.error(request, '❌ Error al crear el proveedor.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para crear el proveedor.'
            )
            if response:
                return response
    else:
        form = SupplierForm()
    
    context = {
        'page_title': 'Crear Proveedor',
        'active_page': 'suppliers',
        'form': form
    }
    
    # Esta vista (supplier_form.html) se mantiene como fallback
    return render(request, 'sigve/supplier_form.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def supplier_edit(request, supplier_id):
    """Editar un proveedor."""
    supplier = CatalogService.get_supplier(supplier_id)
    
    if not supplier:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Proveedor no encontrado.'})
        messages.error(request, '❌ Proveedor no encontrado.')
        return redirect('sigve:suppliers_list')
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
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
                message = '✅ Proveedor actualizado correctamente.'
                if is_ajax:
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'reload_page': True})
                
                messages.success(request, message)
                return redirect('sigve:suppliers_list')
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el proveedor.']}})
                messages.error(request, '❌ Error al actualizar el proveedor.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para actualizar el proveedor.'
            )
            if response:
                return response
    else:
        form = SupplierForm(initial=supplier)
    
    context = {
        'page_title': 'Editar Proveedor',
        'active_page': 'suppliers',
        'form': form,
        'supplier': supplier
    }
    
    # Esta vista (supplier_form.html) se mantiene como fallback
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
    'vehicle_type': {
        'name': 'Tipos de Vehículo', 
        'singular': 'Tipo de Vehículo', 
        'icon': 'bi-truck',
        'placeholder': 'Ej: Carro Bomba, Ambulancia'
    },
    'vehicle_status': {
        'name': 'Estados de Vehículo', 
        'singular': 'Estado de Vehículo', 
        'icon': 'bi-check-circle',
        'placeholder': 'Ej: Operativo, En Taller'
    },
    'fuel_type': {
        'name': 'Tipos de Combustible', 
        'singular': 'Tipo de Combustible', 
        'icon': 'bi-fuel-pump',
        'placeholder': 'Ej: Gasolina 95, Diesel'
    },
    'transmission_type': {
        'name': 'Tipos de Transmisión', 
        'singular': 'Tipo de Transmisión', 
        'icon': 'bi-gear',
        'placeholder': 'Ej: Manual, Automática'
    },
    'oil_type': {
        'name': 'Tipos de Aceite', 
        'singular': 'Tipo de Aceite', 
        'icon': 'bi-water',
        'placeholder': 'Ej: 10W-40 Sintético'
    },
    'coolant_type': {
        'name': 'Tipos de Refrigerante', 
        'singular': 'Tipo de Refrigerante', 
        'icon': 'bi-thermometer-half',
        'placeholder': 'Ej: Orgánico (Rojo)'
    },
    'task_type': {
        'name': 'Tipos de Tarea', 
        'singular': 'Tipo de Tarea', 
        'icon': 'bi-card-checklist',
        'placeholder': 'Ej: Cambio de Aceite'
    },
    'role': {
        'name': 'Roles de Usuario', 
        'singular': 'Rol', 
        'icon': 'bi-person-badge',
        'placeholder': 'Ej: Admin Taller, Conductor'
    },
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
        'catalog_singular_name': config['singular'],
        'catalog_icon': config.get('icon', 'bi-list-ul'),
        'catalog_placeholder': config.get('placeholder', 'Ej: Nuevo Item'),
        'items': CatalogService.get_catalog_items(catalog_name)
    }
    
    return render(request, 'sigve/catalog_list.html', context)


@require_supabase_login
@require_role("Admin SIGVE")
def catalog_create(request, catalog_name):
    """Crear un item de catálogo (ahora compatible con AJAX)."""
    if catalog_name not in CATALOG_CONFIG:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Catálogo no encontrado.'}, status=404)
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    config = CATALOG_CONFIG[catalog_name]
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data.get('description')
            }
            
            item = CatalogService.create_catalog_item(catalog_name, data)
            
            if item:
                message = f'✅ {config["singular"]} creado correctamente.'
                if is_ajax:
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'reload_page': True})
                messages.success(request, message)
                return redirect('sigve:catalog_list', catalog_name=catalog_name)
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el item.']}})
                messages.error(request, '❌ Error al crear el item.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message=f'⚠️ Corrige los errores del formulario para crear {config["singular"]}.'
            )
            if response:
                return response
    else:
        form = CatalogItemForm()
    
    # Fallback para renderizado no-ajax (si se mantiene catalog_form.html)
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
    """Editar un item de catálogo (ahora compatible con AJAX)."""
    if catalog_name not in CATALOG_CONFIG:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Catálogo no encontrado.'}, status=404)
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    config = CATALOG_CONFIG[catalog_name]
    item = CatalogService.get_catalog_item(catalog_name, item_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not item:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Item no encontrado.'}, status=404)
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
                message = '✅ Item actualizado correctamente.'
                if is_ajax:
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'reload_page': True})
                messages.success(request, message)
                return redirect('sigve:catalog_list', catalog_name=catalog_name)
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el item.']}})
                messages.error(request, '❌ Error al actualizar el item.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message=f'⚠️ Corrige los errores del formulario para actualizar {config["singular"]}.'
            )
            if response:
                return response
    else:
        form = CatalogItemForm(initial=item)
    
    # Fallback para renderizado no-ajax (si se mantiene catalog_form.html)
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
    """Eliminar un item de catálogo (ahora compatible con AJAX)."""
    if catalog_name not in CATALOG_CONFIG:
        messages.error(request, '❌ Catálogo no encontrado.')
        return redirect('sigve:dashboard')
    
    success = CatalogService.delete_catalog_item(catalog_name, item_id)
    
    if success:
        messages.success(request, '🗑️ Item eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el item (puede estar en uso).')
    
    # El ConfirmationModal recargará la página, por lo que la redirección es correcta.
    return redirect('sigve:catalog_list', catalog_name=catalog_name)


# ===== GESTIÓN DE USUARIOS =====

@require_supabase_login
@require_role("Admin SIGVE")
def users_list(request):
    """Lista de todos los usuarios de la plataforma."""
    context = {
        'page_title': 'Gestión de Usuarios',
        'active_page': 'users',
        'users': UserService.get_all_users(),
        'roles': UserService.get_all_roles(),
        'workshops': WorkshopService.get_all_workshops(),
        'fire_stations': FireStationService.get_all_fire_stations()
    }
    
    return render(request, 'sigve/users_list.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def user_create(request):
    """Crea un nuevo usuario en Supabase Auth y en user_profile."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    roles = UserService.get_all_roles()
    workshops = WorkshopService.get_all_workshops()
    fire_stations = FireStationService.get_all_fire_stations()

    role_choices = [('', 'Seleccionar rol...')] + [(str(role['id']), role['name']) for role in roles]
    workshop_choices = [('', 'Sin asignar a taller')] + [(str(ws['id']), ws['name']) for ws in workshops]
    fire_station_choices = [('', 'Sin asignar a cuartel')] + [(str(fs['id']), fs['name']) for fs in fire_stations]

    form = UserCreateForm(
        request.POST,
        role_choices=role_choices,
        workshop_choices=workshop_choices,
        fire_station_choices=fire_station_choices
    )

    if form.is_valid():
        cleaned_data = form.cleaned_data
        email = cleaned_data['email']
        password = cleaned_data['password']

        profile_data = {
            'first_name': cleaned_data['first_name'],
            'last_name': cleaned_data['last_name'],
            'rut': cleaned_data.get('rut') or None,
            'phone': cleaned_data.get('phone') or None,
            'role_id': cleaned_data['role_id'],
            'workshop_id': cleaned_data.get('workshop_id'),
            'fire_station_id': cleaned_data.get('fire_station_id'),
            'is_active': cleaned_data.get('is_active', False)
        }

        result = UserService.create_user(
            email=email,
            password=password,
            profile_data=profile_data,
            email_confirm=True,
            metadata={
                'first_name': cleaned_data['first_name'],
                'last_name': cleaned_data['last_name'],
            }
        )

        if result['success']:
            messages.success(request, '✅ Usuario creado correctamente.')
            if is_ajax:
                return JsonResponse({'success': True, 'reload_page': True})
            return redirect('sigve:users_list')

        error_message = result.get('error') or 'Error al crear el usuario.'
        messages.error(request, f'❌ {error_message}')
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'general': [error_message]}})
        return redirect('sigve:users_list')

    response = handle_form_errors(
        request,
        form,
        is_ajax,
        message='⚠️ Corrige los errores del formulario para crear el usuario.'
    )
    if response:
        return response

    return redirect('sigve:users_list')


@require_supabase_login
@require_role("Admin SIGVE")
def user_edit(request, user_id):
    """Editar un usuario."""
    user = UserService.get_user(user_id)
    roles = UserService.get_all_roles()
    workshops = WorkshopService.get_all_workshops()
    fire_stations = FireStationService.get_all_fire_stations()
    
    if not user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'}, status=404)
        messages.error(request, '❌ Usuario no encontrado.')
        return redirect('sigve:users_list')
    
    role_choices = [(str(role['id']), role['name']) for role in roles]
    workshop_choices = [('', 'Sin asignar a taller')] + [(str(ws['id']), ws['name']) for ws in workshops]
    fire_station_choices = [('', 'Sin asignar a cuartel')] + [(str(fs['id']), fs['name']) for fs in fire_stations]
    
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            role_choices=role_choices,
            workshop_choices=workshop_choices,
            fire_station_choices=fire_station_choices
        )
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            cleaned_data = form.cleaned_data
            profile_data = {
                'first_name': cleaned_data['first_name'],
                'last_name': cleaned_data['last_name'],
                'rut': cleaned_data.get('rut'),
                'phone': cleaned_data.get('phone'),
                'role_id': cleaned_data['role_id'],
                'is_active': cleaned_data['is_active'],
                'workshop_id': cleaned_data.get('workshop_id'),
                'fire_station_id': cleaned_data.get('fire_station_id')
            }

            success = UserService.update_user(
                user_id,
                profile_data,
                email=cleaned_data['email']
            )
            
            if success:
                message = '✅ Usuario actualizado correctamente.'
                if is_ajax:
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'reload_page': True})
                
                messages.success(request, message)
                return redirect('sigve:users_list')
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el usuario.']}})
                messages.error(request, '❌ Error al actualizar el usuario.')
        else:
            response = handle_form_errors(
                request,
                form,
                is_ajax,
                message='⚠️ Corrige los errores del formulario para actualizar el usuario.'
            )
            if response:
                return response

    else:
        initial_data = {
            'email': user.get('email'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'rut': user.get('rut'),
            'phone': user.get('phone'),
            'role_id': user.get('role_id'),
            'is_active': user.get('is_active'),
            'workshop_id': user.get('workshop_id'),
            'fire_station_id': user.get('fire_station_id')
        }
        form = UserProfileForm(
            initial=initial_data,
            role_choices=role_choices,
            workshop_choices=workshop_choices,
            fire_station_choices=fire_station_choices
        )
    
    context = {
        'page_title': 'Editar Usuario',
        'active_page': 'users',
        'form': form,
        'user': user,
        'roles': roles,
        'workshops': workshops,
        'fire_stations': fire_stations
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

@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def user_activate(request, user_id):
    """Activa un usuario."""
    success = UserService.activate_user(user_id)
    
    if success:
        messages.success(request, '✅ Usuario activado correctamente.')
    else:
        messages.error(request, '❌ Error al activar el usuario.')
    
    return redirect('sigve:users_list')
    

@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def user_delete(request, user_id):
    """Elimina permanentemente un usuario."""
    
    # Evitar que el admin se elimine a sí mismo
    if request.session.get('sb_user_id') == user_id:
        messages.error(request, '❌ No puedes eliminar tu propia cuenta.')
        return redirect('sigve:users_list')
        
    success = UserService.delete_user(user_id)
    
    if success:
        messages.success(request, '🗑️ Usuario eliminado permanentemente.')
    else:
        messages.error(request, '❌ Error al eliminar el usuario (puede que ya no exista).')
    
    return redirect('sigve:users_list')


# ===== GESTIÓN DE TIPOS DE SOLICITUDES =====

@require_supabase_login
@require_role("Admin SIGVE")
def request_types_list(request):
    """Lista de tipos de solicitudes."""
    context = {
        'page_title': 'Tipos de Solicitudes',
        'active_page': 'request_types',
        'request_types': RequestTypeService.get_all_request_types()
    }
    
    return render(request, 'sigve/request_types_list.html', context)


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def request_type_create(request):
    """Crea un nuevo tipo de solicitud."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = RequestTypeForm(request.POST)
    if form.is_valid():
        import json
        
        # Validar que form_schema sea JSON válido
        try:
            form_schema = json.loads(form.cleaned_data['form_schema'])
        except json.JSONDecodeError:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'form_schema': ['El esquema del formulario debe ser JSON válido.']}
                })
            messages.error(request, '❌ El esquema del formulario debe ser JSON válido.')
            return redirect('sigve:request_types_list')
        
        data = {
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data.get('description'),
            'target_table': form.cleaned_data['target_table'],
            'form_schema': form_schema
        }
        
        request_type = RequestTypeService.create_request_type(data)
        
        if request_type:
            message = f'✅ Tipo de solicitud "{data["name"]}" creado correctamente.'
            if is_ajax:
                messages.success(request, message)
                return JsonResponse({'success': True, 'reload_page': True})
            
            messages.success(request, message)
            return redirect('sigve:request_types_list')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': {'general': ['Error al crear el tipo de solicitud.']}})
            messages.error(request, '❌ Error al crear el tipo de solicitud.')
    else:
        response = handle_form_errors(
            request,
            form,
            is_ajax,
            message='⚠️ Corrige los errores del formulario para crear el tipo de solicitud.'
        )
        if response:
            return response
    
    return redirect('sigve:request_types_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def request_type_update(request, request_type_id):
    """Actualiza un tipo de solicitud."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    form = RequestTypeForm(request.POST)
    if form.is_valid():
        import json
        
        # Validar que form_schema sea JSON válido
        try:
            form_schema = json.loads(form.cleaned_data['form_schema'])
        except json.JSONDecodeError:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'form_schema': ['El esquema del formulario debe ser JSON válido.']}
                })
            messages.error(request, '❌ El esquema del formulario debe ser JSON válido.')
            return redirect('sigve:request_types_list')
        
        data = {
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data.get('description'),
            'target_table': form.cleaned_data['target_table'],
            'form_schema': form_schema
        }
        
        success = RequestTypeService.update_request_type(request_type_id, data)
        
        if success:
            message = '✅ Tipo de solicitud actualizado correctamente.'
            if is_ajax:
                messages.success(request, message)
                return JsonResponse({'success': True, 'reload_page': True})
            
            messages.success(request, message)
            return redirect('sigve:request_types_list')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': {'general': ['Error al actualizar el tipo de solicitud.']}})
            messages.error(request, '❌ Error al actualizar el tipo de solicitud.')
    else:
        response = handle_form_errors(
            request,
            form,
            is_ajax,
            message='⚠️ Corrige los errores del formulario para actualizar el tipo de solicitud.'
        )
        if response:
            return response
    
    return redirect('sigve:request_types_list')


@require_http_methods(["POST"])
@require_supabase_login
@require_role("Admin SIGVE")
def request_type_delete(request, request_type_id):
    """Elimina un tipo de solicitud."""
    success = RequestTypeService.delete_request_type(request_type_id)
    
    if success:
        messages.success(request, '🗑️ Tipo de solicitud eliminado.')
    else:
        messages.error(request, '❌ Error al eliminar el tipo de solicitud (puede tener solicitudes asociadas).')
    
    return redirect('sigve:request_types_list')


# ===== API ENDPOINTS =====

@require_supabase_login
@require_role("Admin SIGVE")
def api_get_communes(request):
    """
    API endpoint para obtener todas las comunas con información de provincia y región.
    Utilizado por los modales para cargar opciones dinámicamente.
    """
    communes = FireStationService.get_all_communes()
    
    # Formatear los datos para el frontend
    communes_data = []
    for commune in communes:
        commune_info = {
            'id': commune['id'],
            'name': commune['name'],
            'province_name': commune.get('province', {}).get('name', '') if isinstance(commune.get('province'), dict) else '',
            'region_name': ''
        }
        
        # Obtener la región desde la provincia
        if isinstance(commune.get('province'), dict):
            province_data = commune.get('province')
            if isinstance(province_data.get('region'), dict):
                commune_info['region_name'] = province_data.get('region', {}).get('name', '')
        
        communes_data.append(commune_info)
    
    return JsonResponse({'communes': communes_data})


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_workshop(request, workshop_id):
    """
    API endpoint para obtener los datos de un taller específico.
    """
    workshop = WorkshopService.get_workshop(workshop_id)
    
    if workshop:
        return JsonResponse({
            'success': True,
            'workshop': workshop
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Taller no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_fire_station(request, fire_station_id):
    """
    API endpoint para obtener los datos de un cuartel específico.
    """
    fire_station = FireStationService.get_fire_station(fire_station_id)
    
    if fire_station:
        return JsonResponse({
            'success': True,
            'fire_station': fire_station
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Cuartel no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_spare_part(request, spare_part_id):
    """
    API endpoint para obtener los datos de un repuesto específico.
    """
    spare_part = CatalogService.get_spare_part(spare_part_id)
    
    if spare_part:
        return JsonResponse({
            'success': True,
            'spare_part': spare_part
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Repuesto no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_supplier(request, supplier_id):
    """
    API endpoint para obtener los datos de un proveedor específico.
    """
    supplier = CatalogService.get_supplier(supplier_id)
    
    if supplier:
        return JsonResponse({
            'success': True,
            'supplier': supplier
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Proveedor no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_user(request, user_id):
    """
    API endpoint para obtener los datos de un usuario específico.
    """
    user = UserService.get_user(user_id)
    
    if user:
        return JsonResponse({
            'success': True,
            'user': user
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_catalog_item(request, catalog_name, item_id):
    """
    API endpoint para obtener los datos de un item de catálogo específico.
    """
    if catalog_name not in CATALOG_CONFIG:
        return JsonResponse({
            'success': False,
            'error': 'Catálogo no encontrado'
        }, status=404)
        
    item = CatalogService.get_catalog_item(catalog_name, item_id)
    
    if item:
        return JsonResponse({
            'success': True,
            'item': item
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Item no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_request_type(request, request_type_id):
    """
    API endpoint para obtener los datos de un tipo de solicitud específico.
    """
    request_type = RequestTypeService.get_request_type(request_type_id)
    
    if request_type:
        import json
        # Convertir form_schema a string JSON para el frontend
        if 'form_schema' in request_type:
            request_type['form_schema'] = json.dumps(request_type['form_schema'], indent=2)
        
        return JsonResponse({
            'success': True,
            'request_type': request_type
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Tipo de solicitud no encontrado'
        }, status=404)


@require_supabase_login
@require_role("Admin SIGVE")
def api_get_map_locations(request):
    """
    API endpoint para obtener las ubicaciones de todos los talleres y cuarteles para el mapa.
    """
    try:
        workshops = WorkshopService.get_all_workshops()
        fire_stations = FireStationService.get_all_fire_stations()
        
        # Formatear datos para el mapa
        locations = {
            'workshops': [],
            'fire_stations': []
        }
        
        # Procesar talleres
        for workshop in workshops:
            if workshop.get('latitude') and workshop.get('longitude'):
                locations['workshops'].append({
                    'id': workshop['id'],
                    'name': workshop['name'],
                    'address': workshop.get('address', ''),
                    'latitude': float(workshop['latitude']),
                    'longitude': float(workshop['longitude']),
                    'phone': workshop.get('phone', ''),
                    'email': workshop.get('email', '')
                })
        
        # Procesar cuarteles
        for station in fire_stations:
            if station.get('latitude') and station.get('longitude'):
                commune_info = station.get('commune', {})
                commune_name = commune_info.get('name', '') if isinstance(commune_info, dict) else ''
                
                locations['fire_stations'].append({
                    'id': station['id'],
                    'name': station['name'],
                    'address': station.get('address', ''),
                    'latitude': float(station['latitude']),
                    'longitude': float(station['longitude']),
                    'commune': commune_name
                })
        
        return JsonResponse({
            'success': True,
            'locations': locations
        })
    except Exception as e:
        logger.error(f"❌ Error obteniendo ubicaciones para el mapa: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Error al obtener las ubicaciones'
        }, status=500)