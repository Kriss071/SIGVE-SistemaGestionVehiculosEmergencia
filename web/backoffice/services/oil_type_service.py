import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService

logger = logging.getLogger(__name__)

class OilTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Aceite (tabla 'oil_type').
    """

    TABLE_NAME = "oil_type"

    def __init__(self, token: str, refresh_token: str):
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de OilTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_oil_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de aceite, ordenados por nombre.
        """
        logger.info(f"📄 (list_oil_types) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_oil_types")

    def get_oil_type(self, oil_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de aceite por su ID.
        """
        logger.info(f"ℹ️ (get_oil_type) Obteniendo {self.TABLE_NAME} con ID: {oil_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", oil_type_id).maybe_single()
        result = self._execute_query(query, "get_oil_type")
        
        if not result:
            logger.warning(f"⚠️ (get_oil_type) {self.TABLE_NAME} no encontrado: {oil_type_id}")
            return None
            
        logger.info(f"✅ (get_oil_type) {self.TABLE_NAME} encontrado: {oil_type_id}")
        return result

    def create_oil_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo tipo de aceite.
        """
        logger.info(f"➕ (create_oil_type) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_oil_type) Supabase no devolvió datos.")
                return False
                
            logger.info(f"✅ (create_oil_type) {self.TABLE_NAME} creado: {response.data[0].get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ (create_oil_type) Error inesperado: {e}", exc_info=True)
            return False

    def update_oil_type(self, oil_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un tipo de aceite existente.
        """
        logger.info(f"🔄 (update_oil_type) Intentando actualizar {self.TABLE_NAME}: {oil_type_id}")
        data.pop('id', None)
        try:
            response = self.client.table(self.TABLE_NAME).update(data).eq("id", oil_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (update_oil_type) Actualización fallida: {oil_type_id}")
                return False
                
            logger.info(f"✅ (update_oil_type) {self.TABLE_NAME} actualizado: {oil_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_oil_type) Error inesperado: {e}", exc_info=True)
            return False

    def delete_oil_type(self, oil_type_id: int) -> bool:
        """
        Elimina un tipo de aceite.
        """
        logger.info(f"🗑️ (delete_oil_type) Intentando eliminar {self.TABLE_NAME}: {oil_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", oil_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_oil_type) Eliminación fallida: {oil_type_id}")
                return False
                
            logger.info(f"✅ (delete_oil_type) {self.TABLE_NAME} eliminado: {oil_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_oil_type) Error inesperado: {e}", exc_info=True)
            return False