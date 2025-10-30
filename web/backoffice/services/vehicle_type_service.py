import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class VehicleTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Vehículo (tabla 'vehicle_type').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "vehicle_type"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de VehicleTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_vehicle_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de vehículo, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un tipo de vehículo.
        """
        logger.info(f"📄 (list_vehicle_types) Obteniendo lista de tipos de vehículo...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_vehicle_types")

    def get_vehicle_type(self, vehicle_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de vehículo específico por su ID.
        
        Args:
            vehicle_type_id: El ID (int) del tipo de vehículo.
            
        Returns:
            Un diccionario con los datos del tipo de vehículo o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_vehicle_type) Obteniendo tipo de vehículo con ID: {vehicle_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", vehicle_type_id).maybe_single()
        
        result = self._execute_query(query, "get_vehicle_type")
        
        if not result:
            logger.warning(f"⚠️ (get_vehicle_type) Tipo de vehículo no encontrado: {vehicle_type_id}")
            return None
            
        logger.info(f"✅ (get_vehicle_type) Tipo de vehículo encontrado: {vehicle_type_id}")
        return result

    def create_vehicle_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de tipo de vehículo.
        
        Args:
            data: Diccionario con los datos (name, description) del tipo de vehículo.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_vehicle_type) Intentando crear tipo de vehículo: {data.get('name')}")
        try:
            data.pop('id', None) # Asegurarse de que el ID no esté en el insert
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_vehicle_type) Supabase no devolvió datos. Creación fallida.")
                return False
                
            logger.info(f"✅ (create_vehicle_type) Tipo de vehículo creado: {response.data[0].get('id')}")
            return True
        except PostgrestAPIError as e:
            logger.error(f"❌ (create_vehicle_type) Error de API al crear tipo: {e.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ (create_vehicle_type) Error inesperado al crear tipo: {e}", exc_info=True)
            return False

    def update_vehicle_type(self, vehicle_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de tipo de vehículo existente.
        
        Args:
            vehicle_type_id: El ID del tipo de vehículo a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_vehicle_type) Intentando actualizar tipo de vehículo: {vehicle_type_id}")
        data.pop('id', None) # Asegurarse de no intentar actualizar la 'id'
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", vehicle_type_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_vehicle_type) Supabase no devolvió datos. Actualización fallida: {vehicle_type_id}")
                return False
                
            logger.info(f"✅ (update_vehicle_type) Tipo de vehículo actualizado: {vehicle_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_vehicle_type) Error inesperado al actualizar tipo: {e}", exc_info=True)
            return False

    def delete_vehicle_type(self, vehicle_type_id: int) -> bool:
        """
        Elimina un registro de tipo de vehículo.
        
        Args:
            vehicle_type_id: El ID del tipo de vehículo a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_vehicle_type) Intentando eliminar tipo de vehículo: {vehicle_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", vehicle_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_vehicle_type) Supabase no devolvió datos. Eliminación fallida: {vehicle_type_id}")
                return False
                
            logger.info(f"✅ (delete_vehicle_type) Tipo de vehículo eliminado: {vehicle_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_vehicle_type) Error inesperado al eliminar tipo: {e}", exc_info=True)
            return False
