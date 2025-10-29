import logging
from .base import MaintenanceService
from accounts.client.supabase_client import get_supabase_with_user
from shared.services.base_service import BaseService

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)


class SupabaseMaintenanceService(BaseService, MaintenanceService):
    """
    Implementación del servicio de mantenimiento que interactúa con Supabase.
    """

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.

        Args:
            token: El token de acceso JWT del usuario actual.
            refresh_token: El token de refresco del usuario actual.
        """

        super().__init__(token, refresh_token)

    def list_maintenance(self):
        """
        Obtiene una lista de todas las órdenes de mantenimiento desde Supabase.

        Realiza una consulta a la tabla 'maintenance_order' y trae información
        relacionada de las tablas de vehículos, talleres y empleados.
        Normaliza los datos anidados en una estructura plana para facilitar su uso.

        Returns:
            list: Una lista de diccionarios, donde cada uno representa una orden
                  de mantenimiento con sus datos relacionados aplanados.
                  Retorna una lista vacía si ocurre un error.
        """
        logger.info("🛠️ (list_maintenance) Obteniendo lista de mantenciones...")
        try:
            # La consulta pide todos los campos de 'maintenance_order' y anida
            # información específica de las tablas relacionadas.
            response = (
                self.client.table("maintenance_order")
                .select(
                    """
                    *,
                    vehicle:vehicle_id(license_plate, brand, model, vehicle_status:vehicle_status_id(name)),
                    workshop:workshop_id(name, address),
                    employee:employee_id(first_name, last_name)
                    """
                )
                .order("entry_date", desc=True)
                .execute()
            )
            logger.debug(f"📊 (list_maintenance) Respuesta cruda de Supabase: {response.data}")

            # Proceso de normalización: Aplanar los datos anidados para un uso más fácil en las plantillas.
            maintenance_orders = []
            for item in response.data:
                # Extraer y aplanar información del vehículo
                vehicle_data = item.get('vehicle', {})
                if isinstance(vehicle_data, dict):
                    item['vehicle_license_plate'] = vehicle_data.get('license_plate', 'N/A')
                    status_data = vehicle_data.get('vehicle_status', {})
                    item['estado_mantencion'] = status_data.get('name', 'Desconocido') if isinstance(status_data, dict) else 'Desconocido'
                else:
                    item['vehicle_license_plate'] = 'N/A'
                    item['estado_mantencion'] = 'Desconocido'

                # Extraer y aplanar información del mecánico (empleado)
                employee_data = item.get('employee', {})
                if isinstance(employee_data, dict):
                    first_name = employee_data.get('first_name', '')
                    last_name = employee_data.get('last_name', '')
                    item['mecanico_nombre_completo'] = f"{first_name} {last_name}".strip()
                else:
                    item['mecanico_nombre_completo'] = 'No asignado'
                
                # Simplificar nombres de campos para la plantilla
                item['observacion'] = item.get('observations')
                item['fecha_ingreso'] = item.get('entry_date')
                item['fecha_salida'] = item.get('exit_date')

                maintenance_orders.append(item)
            
            logger.info(f"✅ (list_maintenance) Se procesaron {len(maintenance_orders)} órdenes de mantenimiento.")
            return maintenance_orders
        except Exception as e:
            logger.error(f"❌ (list_maintenance) Error al obtener mantenciones: {e}", exc_info=True)
            return []
