import logging
from django.contrib import messages
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from accounts.decorators import require_role, require_supabase_login
from .services.role_services import SupabaseRoleService
from .services.employee_service import EmployeeService
from .forms import EmployeeForm
from .services.workshop_service import WorkshopService
from .forms import EmployeeForm, WorkshopForm
from .services.supplier_service import SupplierService
from .forms import EmployeeForm, WorkshopForm, SupplierForm
from .services.vehicle_type_service import VehicleTypeService
from .forms import EmployeeForm, WorkshopForm, SupplierForm, VehicleTypeForm
from .services.fire_station_service import FireStationService
from .forms import FireStationForm
from vehicles.services.catalog_service import CatalogService

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

# Rol requerido para acceder a todo el backoffice
BACKOFFICE_REQUIRED_ROLE = "Administrador"

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def dashboard_view(request):
    """
    Renderiza la página principal (dashboard) del panel de administración.
    """
    logger.info(f"▶️ (dashboard_view) Accediendo al dashboard. Usuario: {request.session.get('sb_user_email')}")
    context = {
        'user_role': request.session.get('sb_user_role', 'Desconocido')
    }
    return render(request, 'backoffice/dashboard.html', context)


# --- Vistas de Roles ---

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def role_list_view(request):
    """
    Muestra la lista de roles.
    """
    logger.info("📄 (role_list_view) Accediendo a la lista de roles.")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseRoleService(token, refresh_token)
    roles = service.list_roles()

    context = {
        'roles': roles,
    }
    return render(request, 'backoffice/role_list.html', context)

# --- Vistas de Empleados ---

def _get_employee_service(request) -> EmployeeService:
    """Función auxiliar para instanciar el servicio con tokens de sesión."""
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    return EmployeeService(token, refresh_token)

def _populate_employee_form(form: EmployeeForm, service: EmployeeService):
    """Función auxiliar para poblar los <select> del formulario."""
    form.set_roles(service.get_roles())
    form.set_workshops(service.get_workshops())

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def employee_list_view(request):
    """
    Renderiza la página de gestión de empleados.
    Muestra la lista y los modales de creación y edición.
    """
    logger.info(f"▶️ (employee_list_view) Accediendo a gestión de empleados. Usuario: {request.session.get('sb_user_email')}")
    service = _get_employee_service(request)
    
    # Obtener lista de empleados
    employees = service.list_employees()
    
    # Preparar formulario de Creación
    create_form = EmployeeForm()
    _populate_employee_form(create_form, service)
    
    # Preparar formulario de Edición (con prefijo "update")
    update_form = EmployeeForm(prefix="update")
    _populate_employee_form(update_form, service)

    context = {
        'employees': employees,
        'create_form': create_form,
        'update_form': update_form,
    }
    return render(request, 'backoffice/employee_list.html', context)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def employee_create_view(request):
    """
    Vista para procesar la creación de un nuevo empleado (desde el modal).
    Primero crea el usuario en Supabase Auth, luego crea el perfil local.
    """
    logger.info("➕ (employee_create_view) Recibida petición POST para crear empleado y usuario.")
    service = _get_employee_service(request)
    form = EmployeeForm(request.POST)
    _populate_employee_form(form, service) # Poblar choices por si falla la validación

    if form.is_valid():
        data = form.cleaned_data
        email = data.pop('email')
        password = data.pop('password')
        
        logger.debug(f"ℹ️ Email: {email}, Password: {password}")

        # Intentar crear el usuario en Supabase Auth
        new_user = service.create_auth_user(email, password)

        if new_user:
            # Si el usuario se creó, Supabase nos da su ID (UUID)
            data['id'] = new_user.id 
            logger.debug(f"ℹ️ Usuario creado en Auth con ID: {data['id']}. Creando perfil de empleado...")
            
            # Crear el perfil del empleado con el ID obtenido
            success = service.create_employee(data)
            if success:
                messages.success(request, f"Usuario y perfil para '{data['first_name']}' creados exitosamente. ✅")
            else:
                # Opcional: Aquí podrías intentar borrar el usuario de Auth si la creación del perfil falla.
                messages.error(request, "El usuario se creó en Supabase, pero falló la creación del perfil local. ❌")
        else:
            messages.error(request, "Error al crear el usuario en Supabase. Es posible que el email ya exista. ❌")
    else:
        logger.warning(f"⚠️ (employee_create_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:employee_list')


@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def employee_update_view(request, employee_id: str):
    """
    Vista para procesar la actualización de un empleado (desde el modal).
    """
    logger.info(f"🔄 (employee_update_view) Recibida petición POST para actualizar empleado: {employee_id}")
    service = _get_employee_service(request)
    form = EmployeeForm(request.POST, prefix="update")
    _populate_employee_form(form, service)

    if form.is_valid():
        data = form.cleaned_data
        # Convertir IDs de choice a int (o None si está vacío)
        data['role_id'] = int(data['role_id']) if data.get('role_id') else None
        data['workshop_id'] = int(data['workshop_id']) if data.get('workshop_id') else None
        
        logger.debug(f"ℹ️ (employee_update_view) Formulario válido. Datos a actualizar: {data}")
        success = service.update_employee(employee_id, data)
        if success:
            messages.success(request, f"Empleado '{data['first_name']} {data['last_name']}' actualizado exitosamente. ✅")
        else:
            messages.error(request, "Error al actualizar el empleado. ❌")
    else:
        logger.warning(f"⚠️ (employee_update_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:employee_list')


@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def employee_delete_view(request, employee_id: str):
    """
    Vista para procesar la eliminación de un empleado (desde el modal).
    """
    logger.info(f"🗑️ (employee_delete_view) Recibida petición POST para eliminar empleado: {employee_id}")
    service = _get_employee_service(request)
    
    success = service.delete_employee(employee_id)
    if success:
        messages.success(request, "Empleado eliminado exitosamente. ✅")
    else:
        messages.error(request, "Error al eliminar el empleado. ❌")
        
    return redirect('backoffice:employee_list')


# --- API (para el modal de edición) ---

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["GET"])
def get_employee_api(request, employee_id: str):
    """
    Endpoint de API para obtener los datos de un empleado y
    poblar el formulario de edición.
    """
    logger.info(f"📡 (get_employee_api) Solicitando datos para empleado: {employee_id}")
    service = _get_employee_service(request)
    employee = service.get_employee(employee_id)
    
    if not employee:
        logger.warning(f"📡 (get_employee_api) Empleado no encontrado: {employee_id}")
        return HttpResponseNotFound(JsonResponse({"error": "Empleado no encontrado"}))
        
    logger.info(f"📡 (get_employee_api) Datos encontrados. Devolviendo JSON.")
    return JsonResponse(employee)


def _get_workshop_service(request) -> WorkshopService:
    """Función auxiliar para instanciar el servicio de Taller."""
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    return WorkshopService(token, refresh_token)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def workshop_list_view(request):
    """
    Renderiza la página de gestión de talleres.
    Muestra la lista y los modales de creación y edición.
    """
    logger.info(f"▶️ (workshop_list_view) Accediendo a gestión de talleres. Usuario: {request.session.get('sb_user_email')}")
    service = _get_workshop_service(request)
    
    workshops = service.list_workshops()
    
    # Preparar formulario de Creación (sin prefijo)
    create_form = WorkshopForm()
    
    # Preparar formulario de Edición (con prefijo "update")
    update_form = WorkshopForm(prefix="update")

    context = {
        'workshops': workshops,
        'create_form': create_form,
        'update_form': update_form,
    }
    return render(request, 'backoffice/workshop_list.html', context)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def workshop_create_view(request):
    """
    Vista para procesar la creación de un nuevo taller (desde el modal).
    """
    logger.info("➕ (workshop_create_view) Recibida petición POST para crear taller.")
    service = _get_workshop_service(request)
    form = WorkshopForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (workshop_create_view) Formulario válido. Datos: {data}")
        
        success = service.create_workshop(data)
        if success:
            messages.success(request, f"Taller '{data['name']}' creado exitosamente. ✅")
        else:
            messages.error(request, "Error al crear el taller. Revise los logs. ❌")
    else:
        logger.warning(f"⚠️ (workshop_create_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:workshop_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def workshop_update_view(request, workshop_id: int):
    """
    Vista para procesar la actualización de un taller (desde el modal).
    """
    logger.info(f"🔄 (workshop_update_view) Recibida petición POST para actualizar taller: {workshop_id}")
    service = _get_workshop_service(request)
    form = WorkshopForm(request.POST, prefix="update")

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (workshop_update_view) Formulario válido. Datos a actualizar: {data}")
        success = service.update_workshop(workshop_id, data)
        if success:
            messages.success(request, f"Taller '{data['name']}' actualizado exitosamente. ✅")
        else:
            messages.error(request, "Error al actualizar el taller. ❌")
    else:
        logger.warning(f"⚠️ (workshop_update_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:workshop_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def workshop_delete_view(request, workshop_id: int):
    """
    Vista para procesar la eliminación de un taller (desde el modal).
    """
    logger.info(f"🗑️ (workshop_delete_view) Recibida petición POST para eliminar taller: {workshop_id}")
    service = _get_workshop_service(request)
    
    success = service.delete_workshop(workshop_id)
    if success:
        messages.success(request, "Taller eliminado exitosamente. ✅")
    else:
        messages.error(request, "Error al eliminar el taller. Es posible que esté en uso. ❌")
        
    return redirect('backoffice:workshop_list')

# --- API (para el modal de edición de Taller) ---

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["GET"])
def get_workshop_api(request, workshop_id: int):
    """
    Endpoint de API para obtener los datos de un taller y
    poblar el formulario de edición.
    """
    logger.info(f"📡 (get_workshop_api) Solicitando datos para taller: {workshop_id}")
    service = _get_workshop_service(request)
    workshop = service.get_workshop(workshop_id)
    
    if not workshop:
        logger.warning(f"📡 (get_workshop_api) Taller no encontrado: {workshop_id}")
        return HttpResponseNotFound(JsonResponse({"error": "Taller no encontrado"}))
        
    logger.info(f"📡 (get_workshop_api) Datos encontrados. Devolviendo JSON.")
    return JsonResponse(workshop)


def _get_supplier_service(request) -> SupplierService:
    """Función auxiliar para instanciar el servicio de Proveedor."""
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    return SupplierService(token, refresh_token)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def supplier_list_view(request):
    """
    Renderiza la página de gestión de proveedores.
    Muestra la lista y los modales de creación y edición.
    """
    logger.info(f"▶️ (supplier_list_view) Accediendo a gestión de proveedores. Usuario: {request.session.get('sb_user_email')}")
    service = _get_supplier_service(request)
    
    suppliers = service.list_suppliers()
    
    # Preparar formulario de Creación (sin prefijo)
    create_form = SupplierForm()
    
    # Preparar formulario de Edición (con prefijo "update")
    update_form = SupplierForm(prefix="update")

    context = {
        'suppliers': suppliers,
        'create_form': create_form,
        'update_form': update_form,
    }
    return render(request, 'backoffice/supplier_list.html', context)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def supplier_create_view(request):
    """
    Vista para procesar la creación de un nuevo proveedor (desde el modal).
    """
    logger.info("➕ (supplier_create_view) Recibida petición POST para crear proveedor.")
    service = _get_supplier_service(request)
    form = SupplierForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (supplier_create_view) Formulario válido. Datos: {data}")
        
        success = service.create_supplier(data)
        if success:
            messages.success(request, f"Proveedor '{data['name']}' creado exitosamente. ✅")
        else:
            messages.error(request, "Error al crear el proveedor. Revise los logs. ❌")
    else:
        logger.warning(f"⚠️ (supplier_create_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:supplier_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def supplier_update_view(request, supplier_id: int):
    """
    Vista para procesar la actualización de un proveedor (desde el modal).
    """
    logger.info(f"🔄 (supplier_update_view) Recibida petición POST para actualizar proveedor: {supplier_id}")
    service = _get_supplier_service(request)
    form = SupplierForm(request.POST, prefix="update")

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (supplier_update_view) Formulario válido. Datos a actualizar: {data}")
        success = service.update_supplier(supplier_id, data)
        if success:
            messages.success(request, f"Proveedor '{data['name']}' actualizado exitosamente. ✅")
        else:
            messages.error(request, "Error al actualizar el proveedor. ❌")
    else:
        logger.warning(f"⚠️ (supplier_update_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:supplier_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def supplier_delete_view(request, supplier_id: int):
    """
    Vista para procesar la eliminación de un proveedor (desde el modal).
    """
    logger.info(f"🗑️ (supplier_delete_view) Recibida petición POST para eliminar proveedor: {supplier_id}")
    service = _get_supplier_service(request)
    
    success = service.delete_supplier(supplier_id)
    if success:
        messages.success(request, "Proveedor eliminado exitosamente. ✅")
    else:
        messages.error(request, "Error al eliminar el proveedor. Es posible que esté en uso. ❌")
        
    return redirect('backoffice:supplier_list')

# --- API (para el modal de edición de Proveedor) ---

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["GET"])
def get_supplier_api(request, supplier_id: int):
    """
    Endpoint de API para obtener los datos de un proveedor y
    poblar el formulario de edición.
    """
    logger.info(f"📡 (get_supplier_api) Solicitando datos para proveedor: {supplier_id}")
    service = _get_supplier_service(request)
    supplier = service.get_supplier(supplier_id)
    
    if not supplier:
        logger.warning(f"📡 (get_supplier_api) Proveedor no encontrado: {supplier_id}")
        return HttpResponseNotFound(JsonResponse({"error": "Proveedor no encontrado"}))
        
    logger.info(f"📡 (get_supplier_api) Datos encontrados. Devolviendo JSON.")
    return JsonResponse(supplier)


def _get_vehicle_type_service(request) -> VehicleTypeService:
    """Función auxiliar para instanciar el servicio de Tipo de Vehículo."""
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    return VehicleTypeService(token, refresh_token)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def vehicle_type_list_view(request):
    """
    Renderiza la página de gestión de tipos de vehículo.
    """
    logger.info(f"▶️ (vehicle_type_list_view) Accediendo a gestión de tipos de vehículo.")
    service = _get_vehicle_type_service(request)
    
    vehicle_types = service.list_vehicle_types()
    
    create_form = VehicleTypeForm()
    update_form = VehicleTypeForm(prefix="update")

    context = {
        'vehicle_types': vehicle_types,
        'create_form': create_form,
        'update_form': update_form,
    }
    return render(request, 'backoffice/vehicle_type_list.html', context)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def vehicle_type_create_view(request):
    """
    Vista para procesar la creación de un nuevo tipo de vehículo.
    """
    logger.info("➕ (vehicle_type_create_view) Recibida petición POST para crear tipo de vehículo.")
    service = _get_vehicle_type_service(request)
    form = VehicleTypeForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (vehicle_type_create_view) Formulario válido. Datos: {data}")
        
        success = service.create_vehicle_type(data)
        if success:
            messages.success(request, f"Tipo de vehículo '{data['name']}' creado exitosamente. ✅")
        else:
            messages.error(request, "Error al crear el tipo de vehículo. ❌")
    else:
        logger.warning(f"⚠️ (vehicle_type_create_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:vehicle_type_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def vehicle_type_update_view(request, vehicle_type_id: int):
    """
    Vista para procesar la actualización de un tipo de vehículo.
    """
    logger.info(f"🔄 (vehicle_type_update_view) POST para actualizar tipo de vehículo: {vehicle_type_id}")
    service = _get_vehicle_type_service(request)
    form = VehicleTypeForm(request.POST, prefix="update")

    if form.is_valid():
        data = form.cleaned_data
        logger.debug(f"ℹ️ (vehicle_type_update_view) Formulario válido. Datos: {data}")
        success = service.update_vehicle_type(vehicle_type_id, data)
        if success:
            messages.success(request, f"Tipo de vehículo '{data['name']}' actualizado. ✅")
        else:
            messages.error(request, "Error al actualizar el tipo de vehículo. ❌")
    else:
        logger.warning(f"⚠️ (vehicle_type_update_view) Formulario inválido: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
        
    return redirect('backoffice:vehicle_type_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def vehicle_type_delete_view(request, vehicle_type_id: int):
    """
    Vista para procesar la eliminación de un tipo de vehículo.
    """
    logger.info(f"🗑️ (vehicle_type_delete_view) POST para eliminar tipo de vehículo: {vehicle_type_id}")
    service = _get_vehicle_type_service(request)
    
    success = service.delete_vehicle_type(vehicle_type_id)
    if success:
        messages.success(request, "Tipo de vehículo eliminado exitosamente. ✅")
    else:
        messages.error(request, "Error al eliminar. Es posible que esté en uso. ❌")
        
    return redirect('backoffice:vehicle_type_list')

# --- API (para el modal de edición de Tipo de Vehículo) ---

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["GET"])
def get_vehicle_type_api(request, vehicle_type_id: int):
    """
    Endpoint de API para obtener los datos de un tipo de vehículo.
    """
    logger.info(f"📡 (get_vehicle_type_api) Solicitando datos para tipo: {vehicle_type_id}")
    service = _get_vehicle_type_service(request)
    vehicle_type = service.get_vehicle_type(vehicle_type_id)
    
    if not vehicle_type:
        logger.warning(f"📡 (get_vehicle_type_api) Tipo no encontrado: {vehicle_type_id}")
        return HttpResponseNotFound(JsonResponse({"error": "Tipo de vehículo no encontrado"}))
        
    logger.info(f"📡 (get_vehicle_type_api) Datos encontrados. Devolviendo JSON.")
    return JsonResponse(vehicle_type)


def _get_fire_station_service(request) -> FireStationService:
    """Función auxiliar para instanciar el servicio de Cuartel."""
    logger.debug("🔧 (_get_fire_station_service) Creando instancia de FireStationService.")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    return FireStationService(token, refresh_token)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def fire_station_list_view(request):
    """
    Renderiza la página de gestión de cuarteles.
    """
    logger.info(f"▶️ (fire_station_list_view) Accediendo a gestión de cuarteles.")
    service = _get_fire_station_service(request)
    
    logger.debug("🎨 (fire_station_list_view) Poblando formularios de creación y actualización con comunas.")
    # Preparar formularios y poblar el menú de comunas
    create_form = FireStationForm()
    create_form.set_communes(CatalogService.get_communes())
    
    update_form = FireStationForm(prefix="update")
    update_form.set_communes(CatalogService.get_communes())

    context = {
        'fire_stations': service.list_fire_stations(),
        'create_form': create_form,
        'update_form': update_form,
    }
    logger.debug("✅ (fire_station_list_view) Contexto preparado, renderizando plantilla.")
    return render(request, 'backoffice/fire_station_list.html', context)

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def fire_station_create_view(request):
    """
    Vista para procesar la creación de un nuevo cuartel.
    """
    logger.info("➕ (fire_station_create_view) POST para crear cuartel.")
    service = _get_fire_station_service(request)
    form = FireStationForm(request.POST)
    form.set_communes(CatalogService.get_communes())
    if form.is_valid():
        logger.debug("✅ (fire_station_create_view) Formulario es válido.")
        data = form.cleaned_data
        data['commune_id'] = int(data['commune_id']) if data.get('commune_id') else None
        success = service.create_fire_station(data)
        if success:
            messages.success(request, f"Cuartel '{data['name']}' creado exitosamente. ✅")
        else:
            messages.error(request, "Error al crear el cuartel. ❌")
    else:
        logger.warning(f"⚠️ (fire_station_create_view) Formulario inválido. Errores: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
            
    return redirect('backoffice:fire_station_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def fire_station_update_view(request, fire_station_id: int):
    """
    Vista para procesar la actualización de un cuartel.
    """
    logger.info(f"🔄 (fire_station_update_view) POST para actualizar cuartel: {fire_station_id}")
    service = _get_fire_station_service(request)
    form = FireStationForm(request.POST, prefix="update")
    form.set_communes(CatalogService.get_communes())

    if form.is_valid():
        logger.debug(f"✅ (fire_station_update_view) Formulario de actualización es válido para ID: {fire_station_id}.")
        data = form.cleaned_data
        data['commune_id'] = int(data['commune_id']) if data.get('commune_id') else None

        logger.debug(f"ℹ️ (fire_station_update_view) Datos limpios para actualizar: {data}")
        success = service.update_fire_station(fire_station_id, data)
        if success:
            messages.success(request, f"Cuartel '{data['name']}' actualizado. ✅")
        else:
            messages.error(request, "Error al actualizar. ❌")
    else:
        logger.warning(f"⚠️ (fire_station_update_view) Formulario de actualización inválido. Errores: {form.errors.as_json()}")
        messages.error(request, f"Error de validación. {form.errors.as_text()} ❌")
            
    return redirect('backoffice:fire_station_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["POST"])
def fire_station_delete_view(request, fire_station_id: int):
    """
    Vista para procesar la eliminación de un cuartel.
    """
    logger.info(f"🗑️ (fire_station_delete_view) POST para eliminar cuartel: {fire_station_id}")
    service = _get_fire_station_service(request)
    
    success = service.delete_fire_station(fire_station_id)
    if success:
        messages.success(request, "Cuartel eliminado exitosamente. ✅")
    else:
        messages.error(request, "Error al eliminar. Es posible que esté en uso. ❌")
            
    return redirect('backoffice:fire_station_list')

@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
@require_http_methods(["GET"])
def get_fire_station_api(request, fire_station_id: int):
    """
    Endpoint de API para obtener los datos de un cuartel (para modales).
    """
    logger.info(f"📡 (get_fire_station_api) Solicitando datos para: {fire_station_id}")
    service = _get_fire_station_service(request)
    item = service.get_fire_station(fire_station_id)
    
    if not item:
        logger.warning(f"❓ (get_fire_station_api) No se encontró el cuartel con ID: {fire_station_id}")
        return HttpResponseNotFound(JsonResponse({"error": "Cuartel no encontrado"}))
            
    logger.debug(f"✅ (get_fire_station_api) Datos encontrados para ID {fire_station_id}. Devolviendo JSON.")
    return JsonResponse(item)