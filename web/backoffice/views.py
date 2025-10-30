import logging
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from accounts.decorators import require_role, require_supabase_login
from .services.role_services import SupabaseRoleService
from .services.employee_service import EmployeeService
from .forms import RoleForm, EmployeeForm


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
