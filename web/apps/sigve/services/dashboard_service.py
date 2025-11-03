import logging
from typing import Dict, List, Any
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class DashboardService(SigveBaseService):
    """Servicio para obtener estadísticas del dashboard."""
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        Obtiene las estadísticas principales para el dashboard.
        
        Returns:
            Dict con las estadísticas: total_workshops, total_fire_stations,
            total_vehicles, available_vehicles, in_maintenance_vehicles
        """
        client = SigveBaseService.get_client()
        
        try:
            # Contar talleres
            workshops_count = client.table("workshop").select("id", count="exact").execute()
            total_workshops = workshops_count.count or 0
            
            # Contar cuarteles
            fire_stations_count = client.table("fire_station").select("id", count="exact").execute()
            total_fire_stations = fire_stations_count.count or 0
            
            # Contar vehículos totales
            vehicles_count = client.table("vehicle").select("id", count="exact").execute()
            total_vehicles = vehicles_count.count or 0
            
            # Contar vehículos disponibles (necesitamos el ID del estado "Disponible")
            # Primero obtenemos el estado
            available_status = client.table("vehicle_status").select("id").eq("name", "Disponible").maybe_single().execute()
            available_vehicles = 0
            if available_status.data:
                available_count = client.table("vehicle").select("id", count="exact").eq("vehicle_status_id", available_status.data['id']).execute()
                available_vehicles = available_count.count or 0
            
            # Contar vehículos en mantención
            maintenance_status = client.table("vehicle_status").select("id").eq("name", "En Mantención").maybe_single().execute()
            in_maintenance_vehicles = 0
            if maintenance_status.data:
                maintenance_count = client.table("vehicle").select("id", count="exact").eq("vehicle_status_id", maintenance_status.data['id']).execute()
                in_maintenance_vehicles = maintenance_count.count or 0
            
            logger.info(f"📊 Estadísticas obtenidas: {total_workshops} talleres, {total_fire_stations} cuarteles, {total_vehicles} vehículos")
            
            return {
                'total_workshops': total_workshops,
                'total_fire_stations': total_fire_stations,
                'total_vehicles': total_vehicles,
                'available_vehicles': available_vehicles,
                'in_maintenance_vehicles': in_maintenance_vehicles
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}", exc_info=True)
            return {
                'total_workshops': 0,
                'total_fire_stations': 0,
                'total_vehicles': 0,
                'available_vehicles': 0,
                'in_maintenance_vehicles': 0
            }
    
    @staticmethod
    def get_recent_activity(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene la actividad reciente del sistema.
        
        Args:
            limit: Número máximo de actividades a retornar.
            
        Returns:
            Lista de actividades recientes.
        """
        client = SigveBaseService.get_client()
        
        try:
            # Obtener las últimas órdenes de mantenimiento creadas
            maintenance_orders = client.table("maintenance_order") \
                .select("id, entry_date, created_at, vehicle:vehicle_id(license_plate, brand, model), workshop:workshop_id(name)") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            activities = []
            if maintenance_orders.data:
                for order in maintenance_orders.data:
                    vehicle_info = order.get('vehicle', {})
                    workshop_info = order.get('workshop', {})
                    activities.append({
                        'type': 'maintenance_order',
                        'description': f"Nueva orden de mantención para {vehicle_info.get('brand', '')} {vehicle_info.get('model', '')} ({vehicle_info.get('license_plate', '')}) en {workshop_info.get('name', 'Taller')}",
                        'date': order.get('created_at', order.get('entry_date'))
                    })
            
            logger.info(f"📋 Actividad reciente obtenida: {len(activities)} registros")
            return activities
        except Exception as e:
            logger.error(f"❌ Error obteniendo actividad reciente: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_pending_requests_count() -> int:
        """
        Obtiene el número de solicitudes pendientes.
        
        Returns:
            Número de solicitudes pendientes.
        """
        client = SigveBaseService.get_client()
        
        try:
            pending_count = client.table("data_request") \
                .select("id", count="exact") \
                .eq("status", "pendiente") \
                .execute()
            
            count = pending_count.count or 0
            logger.info(f"📬 Solicitudes pendientes: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ Error obteniendo solicitudes pendientes: {e}", exc_info=True)
            return 0


