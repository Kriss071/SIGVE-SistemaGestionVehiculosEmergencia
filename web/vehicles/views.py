import logging
from datetime import date
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from .services.vehicle_service import SupabaseVehicleService
from .services.catalog_service import CatalogService
from accounts.decorators import require_role, require_supabase_login
from django.views.decorators.http import require_http_methods
from .forms import VehicleForm

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)


def _populate_form_with_catalogs(form: VehicleForm):
    """
    Función auxiliar para poblar un formulario de vehículo con datos de los catálogos.

    Centraliza la lógica de obtener todos los catálogos necesarios y
    asignarlos a los campos correspondientes del formulario.

    Args:
        form (VehicleForm): La instancia del formulario a poblar.
    """

    logger.debug("🎨 (populate_form) Poblando formulario con datos de catálogos...")
    try:
        form.set_fire_stations(CatalogService.get_fire_stations())
        form.set_vehicle_types(CatalogService.get_vehicle_types())
        form.set_vehicle_statuses(CatalogService.get_vehicle_statuses())
        form.set_fuel_types(CatalogService.get_fuel_types())
        form.set_transmission_types(CatalogService.get_transmission_types())
        form.set_oil_types(CatalogService.get_oil_types())
        form.set_coolant_types(CatalogService.get_coolant_types())
        logger.info("✅ (populate_form) Formulario poblado exitosamente.")
    except Exception as e:
        # Registra el error si la carga de catálogos falla.
        logger.error(f"❌ (populate_form) Error al obtener catálogos para el formulario: {e}", exc_info=True)


@require_supabase_login
def vehicle_list_view(request):
    """
    Renderiza la página principal con el listado de vehículos.

    Obtiene la lista de vehículos (o resultados de búsqueda si hay un parámetro 'q')
    y prepara el formulario de creación de vehículo con todos los catálogos necesarios
    para ser utilizado en un modal.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponse: La página renderizada de la lista de vehículos.
    """

    logger.debug(f"▶️ (vehicle_list_view) Accediendo a la lista de vehículos. Usuario: {request.session.get('sb_user_email')}")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    query = request.GET.get("q", "").strip()
    if query:
        logger.info(f"🔍 (vehicle_list_view) Realizando búsqueda de vehículos con query: '{query}'")
        vehicles = service.search_vehicles(query)
    else:
        logger.info("📄 (vehicle_list_view) Obteniendo la lista completa de vehículos.")
        vehicles = service.list_vehicles()

    user_role = request.session.get("sb_user_role", "Usuario")
    logger.debug(f"🎭 (vehicle_list_view) Rol del usuario: {user_role}")
    
    # Preparar formulario con catálogos para el modal
    form = VehicleForm()
    _populate_form_with_catalogs(form)

    context = {
        "vehicles": vehicles,
        "user_role": user_role,
        "query": query,
        "form": form
    }

    return render(request, "vehicles/vehicle_list.html", context)


@require_supabase_login
def vehicle_search_api(request):
    """
    Endpoint de API para buscar vehículos de forma asíncrona.

    Recibe un parámetro de consulta 'q' y devuelve una lista de vehículos
    en formato JSON. Utilizado por el JavaScript del frontend.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        JsonResponse: Un objeto JSON con la clave 'vehicles' y la lista de resultados.
    """

    query = request.GET.get("q", "")
    logger.info(f"📡 (vehicle_search_api) Búsqueda API iniciada con query: '{query}'")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    results = service.search_vehicles(query)
    logger.info(f"✅ (vehicle_search_api) Búsqueda completada, {len(results)} vehículos encontrados.")
    return JsonResponse({"vehicles": results})


@require_supabase_login
@require_role("Administrador")
@require_http_methods(["GET", "POST"])
def add_vehicle_view(request):
    """
    Gestiona la creación de un nuevo vehículo a través de una petición POST.

    Procesa los datos del formulario, los valida y los envía al servicio para
    crear el vehículo. Muestra mensajes de éxito o error.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponseRedirect: Redirige a la lista de vehículos.
    """

    logger.debug("➕ (add_vehicle_view) Petición POST recibida para agregar vehículo.")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    form = VehicleForm(request.POST if request.method == "POST" else None)
    _populate_form_with_catalogs(form)
    
    if form.is_valid():
        logger.info("✅ (add_vehicle_view) El formulario para agregar vehículo es válido.")
        data = form.cleaned_data

        # Procesa los datos para asegurar que los tipos son correctos antes de enviarlos.
        for key in ['fire_station_id', 'vehicle_type_id', 'vehicle_status_id', 'fuel_type_id', 'transmission_type_id', 'oil_type_id', 'coolant_type_id']:
            if data.get(key):
                data[key] = int(data[key])
            else:
                data[key] = None

        # Elimina claves con strings vacíos que corresponden a campos opcionales.
        for key, value in list(data.items()):
            if isinstance(value, str) and not value.strip():
                data[key] = None

        logger.debug(f"🔧 (add_vehicle_view) Datos procesados para enviar al servicio: {data}")

        try:
            result = service.add_vehicle(data)
            if result:
                messages.success(request, f"Vehículo '{data['license_plate']}' agregado correctamente ✅")
            else:
                messages.error(request, "Error: El servicio no pudo agregar el vehículo. ❌")
        except Exception as e:
            logger.error(f"❌ (add_vehicle_view) Excepción al agregar vehículo: {e}", exc_info=True)
            messages.error(request, f"Error inesperado al agregar vehículo: {e} ❌")
    else:
        # Si el formulario no es válido, se registran los errores.
        logger.warning(f"⚠️ (add_vehicle_view) Formulario inválido. Errores: {form.errors.as_json()}")
        messages.error(request, f"Datos inválidos. Por favor, revisa el formulario. Errores: {form.errors.as_text()}")

    return redirect("vehicle_list")


@require_supabase_login
def vehicle_detail_api(request):
    """
    Endpoint de API para obtener los detalles de un vehículo específico.

    Recibe el parámetro 'license_plate' y devuelve todos los datos del
    vehículo en formato JSON.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        JsonResponse: Un objeto JSON con los detalles del vehículo.
        HttpResponseBadRequest: Si falta el parámetro 'license_plate'.
        HttpResponseNotFound: Si no se encuentra el vehículo.
    """
    license_plate = request.GET.get("license_plate")
    if not license_plate:
        logger.warning("🚫 (vehicle_detail_api) Petición sin el parámetro 'license_plate'.")
        return HttpResponseBadRequest("Falta el parámetro 'license_plate'")

    logger.info(f"ℹ️ (vehicle_detail_api) Solicitando detalles para la patente: {license_plate}")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    vehicle = service.get_vehicle(license_plate)
    if not vehicle:
        logger.warning(f"❓ (vehicle_detail_api) Vehículo no encontrado con patente: {license_plate}")
        return HttpResponseNotFound("Vehículo no encontrado")

    logger.info(f"✅ (vehicle_detail_api) Detalles encontrados para: {license_plate}")
    return JsonResponse({"vehicle": vehicle})


@require_supabase_login
@require_role("Administrador")
@require_http_methods(["DELETE", "POST"])
def delete_vehicle_api(request):
    """
    Endpoint de API para eliminar un vehículo.

    Recibe el parámetro 'license_plate' mediante POST o DELETE y elimina
    el vehículo de la base de datos. Solo los administradores pueden
    realizar esta acción.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        JsonResponse: Un objeto JSON con el resultado de la operación.
        HttpResponseBadRequest: Si falta el parámetro 'license_plate'.
        HttpResponseNotFound: Si no se encuentra el vehículo.
    """
    # Obtener license_plate de POST o del cuerpo de DELETE
    if request.method == "POST":
        license_plate = request.POST.get("license_plate") or request.GET.get("license_plate")
    else:  # DELETE
        import json
        try:
            body = json.loads(request.body) if request.body else {}
            license_plate = body.get("license_plate") or request.GET.get("license_plate")
        except json.JSONDecodeError:
            license_plate = request.GET.get("license_plate")

    if not license_plate:
        logger.warning("🚫 (delete_vehicle_api) Petición sin el parámetro 'license_plate'.")
        return HttpResponseBadRequest("Falta el parámetro 'license_plate'")

    logger.info(f"🗑️ (delete_vehicle_api) Eliminando vehículo con patente: {license_plate}")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    success = service.delete_vehicle(license_plate)
    if not success:
        logger.warning(f"❌ (delete_vehicle_api) No se pudo eliminar el vehículo con patente: {license_plate}")
        return HttpResponseNotFound("Vehículo no encontrado o no se pudo eliminar")

    logger.info(f"✅ (delete_vehicle_api) Vehículo eliminado exitosamente: {license_plate}")
    return JsonResponse({"success": True, "message": f"Vehículo '{license_plate}' eliminado correctamente"})


@require_supabase_login
@require_role("Administrador")
@require_http_methods(["PUT", "POST"])
def update_vehicle_api(request):
    """
    Endpoint de API para actualizar un vehículo existente.

    Recibe los datos actualizados del vehículo mediante POST o PUT.
    Solo los administradores pueden realizar esta acción.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        JsonResponse: Un objeto JSON con el resultado de la operación.
        HttpResponseBadRequest: Si faltan parámetros requeridos.
        HttpResponseNotFound: Si no se encuentra el vehículo.
    """
    import json
    
    # Obtener datos según el método
    if request.method == "POST":
        license_plate = request.POST.get("license_plate")
        # Intentar obtener datos como JSON si están en el body
        try:
            if request.body:
                body_data = json.loads(request.body)
                data = body_data
                license_plate = data.get("license_plate", license_plate)
            else:
                data = dict(request.POST)
                # Limpiar listas de valores únicos
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
        except json.JSONDecodeError:
            data = dict(request.POST)
            data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}
    else:  # PUT
        try:
            data = json.loads(request.body) if request.body else {}
            license_plate = data.get("license_plate")
        except json.JSONDecodeError:
            logger.warning("🚫 (update_vehicle_api) Error al decodificar JSON del body.")
            return HttpResponseBadRequest("Datos inválidos")

    if not license_plate:
        logger.warning("🚫 (update_vehicle_api) Petición sin el parámetro 'license_plate'.")
        return HttpResponseBadRequest("Falta el parámetro 'license_plate'")

    logger.info(f"🔄 (update_vehicle_api) Actualizando vehículo con patente: {license_plate}")
    token = request.session.get("sb_access_token")
    refresh_token = request.session.get("sb_refresh_token")
    service = SupabaseVehicleService(token, refresh_token)

    # Procesar los datos para asegurar que los tipos son correctos
    for key in ['fire_station_id', 'vehicle_type_id', 'vehicle_status_id', 'fuel_type_id', 
                'transmission_type_id', 'oil_type_id', 'coolant_type_id']:
        if key in data and data.get(key):
            try:
                data[key] = int(data[key])
            except (ValueError, TypeError):
                data[key] = None
        elif key in data:
            data[key] = None

    # Eliminar claves con strings vacíos
    for key, value in list(data.items()):
        if isinstance(value, str) and not value.strip() and key not in ['license_plate']:
            data[key] = None

    updated_vehicle = service.update_vehicle(license_plate, data)
    
    if not updated_vehicle:
        logger.warning(f"❌ (update_vehicle_api) No se pudo actualizar el vehículo con patente: {license_plate}")
        return HttpResponseNotFound("Vehículo no encontrado o no se pudo actualizar")

    logger.info(f"✅ (update_vehicle_api) Vehículo actualizado exitosamente: {license_plate}")
    return JsonResponse({
        "success": True, 
        "message": f"Vehículo '{license_plate}' actualizado correctamente",
        "vehicle": updated_vehicle
    })