from django.shortcuts import render
from accounts.decorators import require_supabase_login
from .services.maintenance_service import SupabaseMaintenanceService


@require_supabase_login
def maintenance_list_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseMaintenanceService(token, refresh_token)

    maintenances = service.list_maintenance()
    user_role = request.session.get("sb_user_role", "user")

    return render(
        request,
        "maintenance/maintenance_list.html",
        {"maintenances": maintenances, "user_role": user_role},
    )
