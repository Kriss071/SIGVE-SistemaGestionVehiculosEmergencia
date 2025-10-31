import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService

logger = logging.getLogger(__name__)

class TaskTypeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Tipos de Tarea (tabla 'task_type').
    """

    TABLE_NAME = "task_type"

    def __init__(self, token: str, refresh_token: str):
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de TaskTypeService creada para la tabla '{self.TABLE_NAME}'.")

    def list_task_types(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los tipos de tarea, ordenados por nombre.
        """
        logger.info(f"📄 (list_task_types) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_task_types")

    def get_task_type(self, task_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un tipo de tarea por su ID.
        """
        logger.info(f"ℹ️ (get_task_type) Obteniendo {self.TABLE_NAME} con ID: {task_type_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", task_type_id).maybe_single()
        return self._execute_query(query, "get_task_type")

    def create_task_type(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo tipo de tarea.
        """
        logger.info(f"➕ (create_task_type) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"❌ (create_task_type) Error inesperado: {e}", exc_info=True)
            return False

    def update_task_type(self, task_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un tipo de tarea existente.
        """
        logger.info(f"🔄 (update_task_type) Intentando actualizar {self.TABLE_NAME}: {task_type_id}")
        data.pop('id', None)
        try:
            response = self.client.table(self.TABLE_NAME).update(data).eq("id", task_type_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"❌ (update_task_type) Error inesperado: {e}", exc_info=True)
            return False

    def delete_task_type(self, task_type_id: int) -> bool:
        """
        Elimina un tipo de tarea.
        """
        logger.info(f"🗑️ (delete_task_type) Intentando eliminar {self.TABLE_NAME}: {task_type_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", task_type_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"❌ (delete_task_type) Error inesperado: {e}", exc_info=True)
            return False