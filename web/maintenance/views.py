import logging
from django.shortcuts import render
from accounts.decorators import require_supabase_login
from .services.maintenance_service import SupabaseMaintenanceService

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)

@require_supabase_login
def maintenance_list_view(request):
    """
    Renderiza la página con el listado de todas las órdenes de mantenimiento.

    Utiliza el SupabaseMaintenanceService para obtener los datos y los pasa
    a la plantilla para su visualización.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponse: La página renderizada de la lista de mantenimientos.
    """
    user_email = request.session.get('sb_user_email', 'Usuario desconocido')
    logger.info(f"▶️ (maintenance_list_view) Accediendo a la lista de mantenciones. Usuario: {user_email}")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseMaintenanceService(token, refresh_token)

    maintenances = service.list_maintenance()
    user_role = request.session.get("sb_user_role", "user")

    logger.info(f"📄 (maintenance_list_view) Se encontraron {len(maintenances)} mantenciones para el rol '{user_role}'.")

    context = {
        "maintenances": maintenances,
        "user_role": user_role
    }
    return render(request, "maintenance/maintenance_list.html", context)