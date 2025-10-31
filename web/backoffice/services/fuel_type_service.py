import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class FuelTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Combustible (tabla 'fuel_type').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "fuel_type"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de FuelTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_fuel_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de combustible, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un tipo de combustible.
        """
        logger.info(f"📄 (list_fuel_types) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_fuel_types")

    def get_fuel_type(self, fuel_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de combustible específico por su ID.
        
        Args:
            fuel_type_id: El ID (int) del tipo de combustible.
            
        Returns:
            Un diccionario con los datos del tipo de combustible o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_fuel_type) Obteniendo {self.TABLE_NAME} con ID: {fuel_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", fuel_type_id).maybe_single()
        
        result = self._execute_query(query, "get_fuel_type")
        
        if not result:
            logger.warning(f"⚠️ (get_fuel_type) {self.TABLE_NAME} no encontrado: {fuel_type_id}")
            return None
            
        logger.info(f"✅ (get_fuel_type) {self.TABLE_NAME} encontrado: {fuel_type_id}")
        return result

    def create_fuel_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de tipo de combustible.
        
        Args:
            data: Diccionario con los datos (name, description) del tipo de combustible.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_fuel_type) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_fuel_type) Supabase no devolvió datos.")
                return False
                
            logger.info(f"✅ (create_fuel_type) {self.TABLE_NAME} creado: {response.data[0].get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ (create_fuel_type) Error inesperado: {e}", exc_info=True)
            return False

    def update_fuel_type(self, fuel_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de tipo de combustible existente.
        
        Args:
            fuel_type_id: El ID del tipo de combustible a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_fuel_type) Intentando actualizar {self.TABLE_NAME}: {fuel_type_id}")
        data.pop('id', None)
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", fuel_type_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_fuel_type) Actualización fallida: {fuel_type_id}")
                return False
                
            logger.info(f"✅ (update_fuel_type) {self.TABLE_NAME} actualizado: {fuel_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_fuel_type) Error inesperado: {e}", exc_info=True)
            return False

    def delete_fuel_type(self, fuel_type_id: int) -> bool:
        """
        Elimina un registro de tipo de combustible.
        
        Args:
            fuel_type_id: El ID del tipo de combustible a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_fuel_type) Intentando eliminar {self.TABLE_NAME}: {fuel_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", fuel_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_fuel_type) Eliminación fallida: {fuel_type_id}")
                return False
                
            logger.info(f"✅ (delete_fuel_type) {self.TABLE_NAME} eliminado: {fuel_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_fuel_type) Error inesperado: {e}", exc_info=True)
            return False