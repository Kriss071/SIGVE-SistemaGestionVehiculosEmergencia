from datetime import date
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from .services.vehicle_service import SupabaseVehicleService
from .services.catalog_service import CatalogService
from accounts.decorators import require_role, require_supabase_login
from django.views.decorators.http import require_http_methods
from .forms import VehicleForm


def _populate_form_with_catalogs(form: VehicleForm):
    """Pobla el formulario con datos de los catálogos"""
    try:
        form.set_fire_stations(CatalogService.get_fire_stations())
        form.set_vehicle_types(CatalogService.get_vehicle_types())
        form.set_vehicle_statuses(CatalogService.get_vehicle_statuses())
        form.set_fuel_types(CatalogService.get_fuel_types())
        form.set_transmission_types(CatalogService.get_transmission_types())
        form.set_oil_types(CatalogService.get_oil_types())
        form.set_coolant_types(CatalogService.get_coolant_types())
    except Exception as e:
        print(f"Error al obtener catálogos: {e}")


# Listado de Vehiculos
@require_supabase_login
def vehicle_list_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    query = request.GET.get("q", "").strip()
    if query:
        vehicles = service.search_vehicles(query)
    else:
        vehicles = service.list_vehicles()

    user_role = request.session.get("sb_user_role", "Usuario")
    print(f"Rol en vehicle_list_view: {user_role}")
    
    # Preparar formulario con catálogos para el modal
    form = VehicleForm()
    try:
        catalog_service = CatalogService()
        form.set_fire_stations(catalog_service.get_fire_stations())
        form.set_vehicle_types(catalog_service.get_vehicle_types())
        form.set_vehicle_statuses(catalog_service.get_vehicle_statuses())
        form.set_fuel_types(catalog_service.get_fuel_types())
        form.set_transmission_types(catalog_service.get_transmission_types())
        form.set_oil_types(catalog_service.get_oil_types())
        form.set_coolant_types(catalog_service.get_coolant_types())
    except Exception as e:
        print(f"Error al cargar catálogos en vehicle_list_view: {e}")

    return render(
        request,
        "vehicles/vehicle_list.html",
        {"vehicles": vehicles, "user_role": user_role, "query": query, "form": form},
    )


# Buscardor
@require_supabase_login
def vehicle_search_api(request):
    query = request.GET.get("q", "")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    results = service.search_vehicles(query)
    return JsonResponse({"vehicles": results})


# Agregar Vehiculo
@require_supabase_login
@require_role("Administrador")
@require_http_methods(["GET", "POST"])
def add_vehicle_view(request):
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    # Obtener catálogos
    catalog_service = CatalogService()
    fire_stations = catalog_service.get_fire_stations()
    vehicle_types = catalog_service.get_vehicle_types()
    vehicle_statuses = catalog_service.get_vehicle_statuses()
    fuel_types = catalog_service.get_fuel_types()
    transmission_types = catalog_service.get_transmission_types()
    oil_types = catalog_service.get_oil_types()
    coolant_types = catalog_service.get_coolant_types()

    form = VehicleForm(request.POST if request.method == "POST" else None)
    
    # Poblar formulario con catálogos
    form.set_fire_stations(fire_stations)
    form.set_vehicle_types(vehicle_types)
    form.set_vehicle_statuses(vehicle_statuses)
    form.set_fuel_types(fuel_types)
    form.set_transmission_types(transmission_types)
    form.set_oil_types(oil_types)
    form.set_coolant_types(coolant_types)

    if request.method == "POST" and form.is_valid():
        # Preparar datos para insertar
        data = form.cleaned_data
        
        import logging
        view_logger = logging.getLogger(__name__)
        view_logger.debug(f"🕵️ Datos limpios del formulario antes de enviar al servicio: {data}")

        # Convertir foreign keys a enteros
        data['fire_station_id'] = int(data['fire_station_id']) if data['fire_station_id'] else None
        data['vehicle_type_id'] = int(data['vehicle_type_id']) if data['vehicle_type_id'] else None
        data['vehicle_status_id'] = int(data['vehicle_status_id']) if data['vehicle_status_id'] else None
        data['fuel_type_id'] = int(data['fuel_type_id']) if data.get('fuel_type_id') else None
        data['transmission_type_id'] = int(data['transmission_type_id']) if data.get('transmission_type_id') else None
        data['oil_type_id'] = int(data['oil_type_id']) if data.get('oil_type_id') else None
        data['coolant_type_id'] = int(data['coolant_type_id']) if data.get('coolant_type_id') else None
        
        # Remover campos vacíos de cadenas
        for key, value in list(data.items()):
            if isinstance(value, str) and value == '':
                data.pop(key)

        try:
            result = service.add_vehicle(data)
            if result:
                messages.success(request, "Vehículo agregado correctamente ✅")
            else:
                messages.error(request, "Error al agregar vehículo ❌")
        except Exception as e:
            messages.error(request, f"Error al agregar vehículo: {str(e)} ❌")
        
        return redirect("vehicle_list")
    
    # Para GET, simplemente redirigir a la lista (el formulario se carga dinámicamente en el modal)
    return redirect("vehicle_list")


# Detalle Vehiculo
@require_supabase_login
def vehicle_detail_api(request):
    license_plate = request.GET.get("license_plate") or request.GET.get("patente")
    if not license_plate:
        return HttpResponseBadRequest("Missing 'license_plate' parameter")

    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    vehicle = service.get_vehicle(license_plate)
    if not vehicle:
        return HttpResponseNotFound("Vehículo no encontrado")

    return JsonResponse({"vehicle": vehicle})
