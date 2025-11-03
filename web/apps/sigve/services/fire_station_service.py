import logging
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class FireStationService(SigveBaseService):
    """Servicio para gestionar cuarteles de bomberos."""
    
    @staticmethod
    def get_all_fire_stations() -> List[Dict[str, Any]]:
        """
        Obtiene todos los cuarteles con información adicional.
        
        Returns:
            Lista de cuarteles.
        """
        client = SigveBaseService.get_client()
        query = client.table("fire_station") \
            .select("""
                *,
                commune:commune_id(name, province:province_id(name, region:region_id(name)))
            """) \
            .order("name")
        
        fire_stations = SigveBaseService._execute_query(query, "get_all_fire_stations")
        
        # Contar vehículos para cada cuartel
        for station in fire_stations:
            try:
                vehicles_count = client.table("vehicle") \
                    .select("id", count="exact") \
                    .eq("fire_station_id", station['id']) \
                    .execute()
                station['vehicles_count'] = vehicles_count.count or 0
            except Exception as e:
                logger.error(f"❌ Error contando vehículos del cuartel {station['id']}: {e}")
                station['vehicles_count'] = 0
        
        return fire_stations
    
    @staticmethod
    def get_fire_station(fire_station_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cuartel específico por ID.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            Datos del cuartel o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station") \
                .select("""
                    *,
                    commune:commune_id(name, province:province_id(name, region:region_id(name)))
                """) \
                .eq("id", fire_station_id) \
                .maybe_single() \
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo cuartel {fire_station_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_fire_station(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo cuartel.
        
        Args:
            data: Datos del cuartel (name, address, commune_id).
            
        Returns:
            Datos del cuartel creado o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Cuartel creado: {data.get('name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando cuartel: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_fire_station(fire_station_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un cuartel existente.
        
        Args:
            fire_station_id: ID del cuartel.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station") \
                .update(data) \
                .eq("id", fire_station_id) \
                .execute()
            
            logger.info(f"✅ Cuartel {fire_station_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando cuartel {fire_station_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_fire_station(fire_station_id: int) -> bool:
        """
        Elimina un cuartel.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station") \
                .delete() \
                .eq("id", fire_station_id) \
                .execute()
            
            logger.info(f"🗑️ Cuartel {fire_station_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando cuartel {fire_station_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_all_communes() -> List[Dict[str, Any]]:
        """
        Obtiene todas las comunas para formularios.
        
        Returns:
            Lista de comunas con provincia y región.
        """
        client = SigveBaseService.get_client()
        query = client.table("commune") \
            .select("""
                *,
                province:province_id(name, region:region_id(name))
            """) \
            .order("name")
        
        return SigveBaseService._execute_query(query, "get_all_communes")


