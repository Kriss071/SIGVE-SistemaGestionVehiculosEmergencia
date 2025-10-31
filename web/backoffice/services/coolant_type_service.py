import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService

logger = logging.getLogger(__name__)

class CoolantTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Refrigerante (tabla 'coolant_type').
    """

    TABLE_NAME = "coolant_type"

    def __init__(self, token: str, refresh_token: str):
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de CoolantTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_coolant_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de refrigerante, ordenados por nombre.
        """
        logger.info(f"📄 (list_coolant_types) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_coolant_types")

    def get_coolant_type(self, coolant_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de refrigerante por su ID.
        """
        logger.info(f"ℹ️ (get_coolant_type) Obteniendo {self.TABLE_NAME} con ID: {coolant_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", coolant_type_id).maybe_single()
        result = self._execute_query(query, "get_coolant_type")
        
        if not result:
            logger.warning(f"⚠️ (get_coolant_type) {self.TABLE_NAME} no encontrado: {coolant_type_id}")
            return None
            
        logger.info(f"✅ (get_coolant_type) {self.TABLE_NAME} encontrado: {coolant_type_id}")
        return result

    def create_coolant_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo tipo de refrigerante.
        """
        logger.info(f"➕ (create_coolant_type) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_coolant_type) Supabase no devolvió datos.")
                return False
                
            logger.info(f"✅ (create_coolant_type) {self.TABLE_NAME} creado: {response.data[0].get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ (create_coolant_type) Error inesperado: {e}", exc_info=True)
            return False

    def update_coolant_type(self, coolant_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un tipo de refrigerante existente.
        """
        logger.info(f"🔄 (update_coolant_type) Intentando actualizar {self.TABLE_NAME}: {coolant_type_id}")
        data.pop('id', None)
        try:
            response = self.client.table(self.TABLE_NAME).update(data).eq("id", coolant_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (update_coolant_type) Actualización fallida: {coolant_type_id}")
                return False
                
            logger.info(f"✅ (update_coolant_type) {self.TABLE_NAME} actualizado: {coolant_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_coolant_type) Error inesperado: {e}", exc_info=True)
            return False

    def delete_coolant_type(self, coolant_type_id: int) -> bool:
        """
        Elimina un tipo de refrigerante.
        """
        logger.info(f"🗑️ (delete_coolant_type) Intentando eliminar {self.TABLE_NAME}: {coolant_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", coolant_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_coolant_type) Eliminación fallida: {coolant_type_id}")
                return False
                
            logger.info(f"✅ (delete_coolant_type) {self.TABLE_NAME} eliminado: {coolant_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_coolant_type) Error inesperado: {e}", exc_info=True)
            return False