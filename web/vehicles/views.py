from datetime import date
from django.contrib import messages
from django.shortcuts import redirect, render
from .services.vehicle_service import SupabaseVehicleService
from accounts.decorators import require_role, require_supabase_login
from django.views.decorators.http import require_http_methods
from .forms import VehicleForm


@require_supabase_login
def vehicle_list_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)
    
    vehicles = service.list_vehicles()
    form = VehicleForm()
    user_role = request.session.get("sb_user_role", "user")

    return render(request, "vehicles/vehicle_list.html", {
        "vehicles": vehicles,
        "form": form,
        "user_role": user_role
    })


@require_supabase_login
@require_role("administrador")
@require_http_methods(["GET", "POST"])
def add_vehicle_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    form = VehicleForm(request.POST)

    if request.method == "POST" and form.is_valid():

        data = form.cleaned_data
        success = service.add_vehicle(data)

        if success:
            messages.success(request, "Vehículo agregado correctamente ✅")
        else:
            messages.error(request, "Error al agregar vehículo ❌")
        return redirect("vehicle_list")
    
    else:
        messages.error(request, "Formulario inválido. Revisa los campos ⚠️")

    return render(request, "form/add_vehicle.html", {"form": form})
