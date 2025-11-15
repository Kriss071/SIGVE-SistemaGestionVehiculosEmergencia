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
        
        # Contar vehículos por estado
        vehicles_available = sum(1 for v in vehicles if v.get('vehicle_status', {}).get('name') == 'Disponible')
        vehicles_in_maintenance = sum(1 for v in vehicles if v.get('vehicle_status', {}).get('name') == 'En Mantención')
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

