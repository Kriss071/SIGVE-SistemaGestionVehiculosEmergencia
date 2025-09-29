from django.shortcuts import render
from .services.supabase_service import SupabaseVehicleService
from accounts.decorators import require_supabase_login

@require_supabase_login
def vehicle_list_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)
    vehicles = service.list_vehicles()
    return render(request, "vehicles/vehicle_list.html", {"vehicles": vehicles})
