import logging
from django.shortcuts import render
from accounts.decorators import require_role, require_supabase_login
from .services.role_services import SupabaseRoleService

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
    logger.info(f"▶️ Accediendo al dashboard del backoffice. Usuario: {request.session.get('sb_user_email')}")
    context = {
        'user_role': request.session.get('sb_user_role', 'Desconocido')
    }
    return render(request, 'backoffice/dashboard.html', context)


@require_supabase_login
@require_role(BACKOFFICE_REQUIRED_ROLE)
def role_list_view(request):
    """
    Muestra la lista de todos los roles existentes.
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