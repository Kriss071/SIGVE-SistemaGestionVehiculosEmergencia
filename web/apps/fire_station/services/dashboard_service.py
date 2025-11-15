import logging
from typing import Dict, List, Any
from .base_service import FireStationBaseService

logger = logging.getLogger(__name__)


class DashboardService(FireStationBaseService):
    """
    Servicio para el dashboard del cuartel de bomberos.
    Proporciona estadísticas y datos resumidos.
    """
    
    @classmethod
    def get_statistics(cls, fire_station_id: int) -> Dict[str, Any]:
        """
        Obtiene las estadísticas del cuartel.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            Diccionario con las estadísticas.
        """
        logger.info(f"📊 Obteniendo estadísticas para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        # Obtener todos los vehículos del cuartel
        vehicles = cls._execute_query(
            client.table('vehicle')
                .select('*, vehicle_status(name)')
                .eq('fire_station_id', fire_station_id),
            'get_statistics_vehicles'
        )
        
        total_vehicles = len(vehicles)
        vehicle_ids = [v.get('id') for v in vehicles if v.get('id')]
        
        # Obtener vehículos con órdenes de mantenimiento activas (en taller)
        # Solo contamos vehículos que pertenecen al cuartel del usuario
        vehicles_in_workshop = set()
        if vehicle_ids:
            try:
                # Crear un set de IDs de vehículos del cuartel para verificación rápida
                vehicle_ids_set = set(vehicle_ids)
                
                # Obtener todas las órdenes de los vehículos del cuartel
                # Incluimos la relación con vehicle para verificar que pertenece al cuartel
                orders = cls._execute_query(
                    client.table('maintenance_order')
                        .select('vehicle_id, exit_date, order_status:order_status_id(name), vehicle:vehicle_id(fire_station_id)')
                        .in_('vehicle_id', vehicle_ids)
                        .order('created_at', desc=True),
                    'get_orders_for_statistics'
                )
                
                # Estados que indican que la orden está completada
                completed_statuses = ['Disponible', 'En Taller', 'De Baja']
                
                # Procesar órdenes y encontrar las activas
                # Verificamos que el vehículo realmente pertenece al cuartel
                for order in orders:
                    vehicle_id = order.get('vehicle_id')
                    
                    # Verificar que el vehículo pertenece al cuartel (doble verificación)
                    vehicle_data = order.get('vehicle', {})
                    if vehicle_data and vehicle_data.get('fire_station_id') != fire_station_id:
                        continue  # El vehículo no pertenece a este cuartel
                    
                    # Verificar que el vehicle_id está en nuestra lista (otra verificación)
                    if vehicle_id not in vehicle_ids_set:
                        continue  # No debería pasar, pero por seguridad
                    
                    if vehicle_id in vehicles_in_workshop:
                        continue  # Ya está marcado como en taller
                    
                    status_name = (order.get('order_status', {}) or {}).get('name', '')
                    exit_date = order.get('exit_date')
                    
                    # Si no tiene fecha de salida y el estado no está completado, está en taller
                    if not exit_date and status_name not in completed_statuses:
                        vehicles_in_workshop.add(vehicle_id)
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo órdenes activas: {e}")
        
        # Contar vehículos por estado
        vehicles_available = sum(1 for v in vehicles if v.get('vehicle_status', {}).get('name') == 'Disponible')
        vehicles_in_maintenance = sum(1 for v in vehicles if v.get('vehicle_status', {}).get('name') == 'En Taller')
        vehicles_out_of_service = sum(1 for v in vehicles if v.get('vehicle_status', {}).get('name') == 'De Baja')
        
        # Vehículos que requieren revisión técnica próxima (simulado)
        vehicles_need_revision = 0
        
        return {
            'total_vehicles': total_vehicles,
            'vehicles_available': vehicles_available,
            'vehicles_in_maintenance': vehicles_in_maintenance,
            'vehicles_out_of_service': vehicles_out_of_service,
            'vehicles_need_revision': vehicles_need_revision,
        }
    
    @classmethod
    def get_recent_vehicles(cls, fire_station_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene los vehículos recientemente agregados o actualizados.
        
        Args:
            fire_station_id: ID del cuartel.
            limit: Número máximo de vehículos a retornar.
            
        Returns:
            Lista de vehículos recientes.
        """
        logger.info(f"📋 Obteniendo vehículos recientes para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        vehicles = cls._execute_query(
            client.table('vehicle')
                .select('*, vehicle_type(name), vehicle_status(name)')
                .eq('fire_station_id', fire_station_id)
                .order('updated_at', desc=True)
                .limit(limit),
            'get_recent_vehicles'
        )
        
        return vehicles
    
    @classmethod
    def get_vehicles_by_type(cls, fire_station_id: int) -> Dict[str, int]:
        """
        Obtiene el conteo de vehículos agrupados por tipo.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            Diccionario con el conteo por tipo de vehículo.
        """
        logger.info(f"📊 Obteniendo vehículos por tipo para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        vehicles = cls._execute_query(
            client.table('vehicle')
                .select('*, vehicle_type(name)')
                .eq('fire_station_id', fire_station_id),
            'get_vehicles_by_type'
        )
        
        # Agrupar por tipo
        type_counts = {}
        for vehicle in vehicles:
            vehicle_type = vehicle.get('vehicle_type', {}).get('name', 'Sin Tipo')
            type_counts[vehicle_type] = type_counts.get(vehicle_type, 0) + 1
        
        return type_counts

