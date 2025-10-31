import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService

logger = logging.getLogger(__name__)

class TransmissionTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Transmisión (tabla 'transmission_type').
    """

    TABLE_NAME = "transmission_type"

    def __init__(self, token: str, refresh_token: str):
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de TransmissionTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_transmission_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de transmisión, ordenados por nombre.
        """
        logger.info(f"📄 (list_transmission_types) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_transmission_types")

    def get_transmission_type(self, transmission_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de transmisión por su ID.
        """
        logger.info(f"ℹ️ (get_transmission_type) Obteniendo {self.TABLE_NAME} con ID: {transmission_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", transmission_type_id).maybe_single()
        result = self._execute_query(query, "get_transmission_type")
        
        if not result:
            logger.warning(f"⚠️ (get_transmission_type) {self.TABLE_NAME} no encontrado: {transmission_type_id}")
            return None
            
        logger.info(f"✅ (get_transmission_type) {self.TABLE_NAME} encontrado: {transmission_type_id}")
        return result

    def create_transmission_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo tipo de transmisión.
        """
        logger.info(f"➕ (create_transmission_type) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_transmission_type) Supabase no devolvió datos.")
                return False
                
            logger.info(f"✅ (create_transmission_type) {self.TABLE_NAME} creado: {response.data[0].get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ (create_transmission_type) Error inesperado: {e}", exc_info=True)
            return False

    def update_transmission_type(self, transmission_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un tipo de transmisión existente.
        """
        logger.info(f"🔄 (update_transmission_type) Intentando actualizar {self.TABLE_NAME}: {transmission_type_id}")
        data.pop('id', None)
        try:
            response = self.client.table(self.TABLE_NAME).update(data).eq("id", transmission_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (update_transmission_type) Actualización fallida: {transmission_type_id}")
                return False
                
            logger.info(f"✅ (update_transmission_type) {self.TABLE_NAME} actualizado: {transmission_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_transmission_type) Error inesperado: {e}", exc_info=True)
            return False

    def delete_transmission_type(self, transmission_type_id: int) -> bool:
        """
        Elimina un tipo de transmisión.
        """
        logger.info(f"🗑️ (delete_transmission_type) Intentando eliminar {self.TABLE_NAME}: {transmission_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", transmission_type_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_transmission_type) Eliminación fallida: {transmission_type_id}")
                return False
                
            logger.info(f"✅ (delete_transmission_type) {self.TABLE_NAME} eliminado: {transmission_type_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_transmission_type) Error inesperado: {e}", exc_info=True)
            return False