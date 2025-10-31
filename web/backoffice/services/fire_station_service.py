import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class FireStationService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Cuarteles de Bomberos (tabla 'fire_station').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "fire_station"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de FireStationService creada para la tabla '{self.TABLE_NAME}'.")

    def list_fire_stations(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los cuarteles de bomberos, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un cuartel.
        """
        logger.info(f"📄 (list_fire_stations) Obteniendo lista de cuarteles...")
        try:
            # Se añade el join para traer el nombre de la comuna
            response = (
                self.client.table(self.TABLE_NAME)
                .select("*, commune:commune_id(name)")
                .order("name")
                .execute()
            )
            logger.debug(f"📊 (list_fire_stations) Respuesta cruda de Supabase: {response.data}")

            # Normalizar los datos para un acceso más fácil en la plantilla
            stations = []
            for item in response.data:
                commune_data = item.get('commune', {})
                item['commune_name'] = commune_data.get('name', 'N/A') if isinstance(commune_data, dict) else 'N/A'
                stations.append(item)
            
            logger.info(f"✅ (list_fire_stations) Se procesaron {len(stations)} cuarteles.")
            return stations
        except Exception as e:
            logger.error(f"❌ (list_fire_stations) Error al obtener cuarteles: {e}", exc_info=True)
            return []

    def get_fire_station(self, fire_station_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un cuartel específico por su ID.
        
        Args:
            fire_station_id: El ID (int) del cuartel.
            
        Returns:
            Un diccionario con los datos del cuartel o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_fire_station) Obteniendo cuartel con ID: {fire_station_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", fire_station_id).maybe_single()
        
        result = self._execute_query(query, "get_fire_station")
        
        if not result:
            logger.warning(f"⚠️ (get_fire_station) Cuartel no encontrado: {fire_station_id}")
            return None
            
        logger.info(f"✅ (get_fire_station) Cuartel encontrado: {fire_station_id}")
        return result

    def create_fire_station(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de cuartel.
        
        Args:
            data: Diccionario con los datos del cuartel a crear.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_fire_station) Intentando crear cuartel con nombre: {data.get('name')}")
        try:
            data.pop('id', None) # Asegurarse de que el ID no esté en el insert
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_fire_station) Supabase no devolvió datos. Creación fallida.")
                return False
                
            logger.info(f"✅ (create_fire_station) Cuartel creado exitosamente: {response.data[0].get('id')}")
            return True
        except PostgrestAPIError as e:
            logger.error(f"❌ (create_fire_station) Error de API al crear cuartel: {e.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ (create_fire_station) Error inesperado al crear cuartel: {e}", exc_info=True)
            return False

    def update_fire_station(self, fire_station_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de cuartel existente.
        
        Args:
            fire_station_id: El ID del cuartel a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_fire_station) Intentando actualizar cuartel: {fire_station_id}")
        data.pop('id', None) # Asegurarse de no intentar actualizar la 'id'
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", fire_station_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_fire_station) Supabase no devolvió datos. Actualización fallida para: {fire_station_id}")
                return False
                
            logger.info(f"✅ (update_fire_station) Cuartel actualizado exitosamente: {fire_station_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_fire_station) Error inesperado al actualizar cuartel: {e}", exc_info=True)
            return False

    def delete_fire_station(self, fire_station_id: int) -> bool:
        """
        Elimina un registro de cuartel.
        
        Args:
            fire_station_id: El ID del cuartel a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_fire_station) Intentando eliminar cuartel: {fire_station_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", fire_station_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_fire_station) Supabase no devolvió datos. Eliminación fallida para: {fire_station_id}")
                return False
                
            logger.info(f"✅ (delete_fire_station) Cuartel eliminado exitosamente: {fire_station_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_fire_station) Error inesperado al eliminar cuartel: {e}", exc_info=True)
            return False