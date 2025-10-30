import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class WorkshopService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Talleres (tabla 'workshop').
    Se conecta con Supabase para operaciones CRUD.
    Hereda de BaseService para obtener el cliente Supabase.
    """

    TABLE_NAME = "workshop"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de WorkshopService creada para la tabla '{self.TABLE_NAME}'.")

    def list_workshops(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los talleres, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un taller.
        """
        logger.info(f"📄 (list_workshops) Obteniendo lista de talleres...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        # Usamos el método _execute_query heredado de BaseService
        return self._execute_query(query, "list_workshops")

    def get_workshop(self, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un taller específico por su ID.
        
        Args:
            workshop_id: El ID (int) del taller.
            
        Returns:
            Un diccionario con los datos del taller o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_workshop) Obteniendo taller con ID: {workshop_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", workshop_id).maybe_single()
        # Usamos _execute_query, que devuelve una lista, y tomamos el primer elemento si existe
        result = self._execute_query(query, "get_workshop")
        if isinstance(result, list): # _execute_query siempre devuelve lista
             logger.warning(f"⚠️ (get_workshop) 'maybe_single' devolvió una lista, se esperaba dict. Datos: {result}")
             return None # Ocurrió un error en _execute_query
        
        # Si la consulta fue exitosa, 'result' será el diccionario o None
        if not result:
            logger.warning(f"⚠️ (get_workshop) Taller no encontrado: {workshop_id}")
            return None
            
        logger.info(f"✅ (get_workshop) Taller encontrado: {workshop_id}")
        return result

    def create_workshop(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de taller.
        
        Args:
            data: Diccionario con los datos del taller a crear 
                  (name, address, phone, email).
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_workshop) Intentando crear taller con nombre: {data.get('name')}")
        try:
            # Quitamos el 'id' si vino en el formulario (no debe estar en el insert)
            data.pop('id', None) 
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_workshop) Supabase no devolvió datos. Creación fallida.")
                return False
                
            logger.info(f"✅ (create_workshop) Taller creado exitosamente: {response.data[0].get('id')}")
            return True
        except PostgrestAPIError as e:
            logger.error(f"❌ (create_workshop) Error de API al crear taller: {e.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ (create_workshop) Error inesperado al crear taller: {e}", exc_info=True)
            return False

    def update_workshop(self, workshop_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de taller existente.
        
        Args:
            workshop_id: El ID del taller a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_workshop) Intentando actualizar taller: {workshop_id}")
        # Asegurarse de no intentar actualizar la 'id'
        data.pop('id', None)
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", workshop_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_workshop) Supabase no devolvió datos. Actualización fallida para: {workshop_id}")
                return False
                
            logger.info(f"✅ (update_workshop) Taller actualizado exitosamente: {workshop_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_workshop) Error inesperado al actualizar taller: {e}", exc_info=True)
            return False

    def delete_workshop(self, workshop_id: int) -> bool:
        """
        Elimina un registro de taller.
        
        Args:
            workshop_id: El ID del taller a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_workshop) Intentando eliminar taller: {workshop_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", workshop_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_workshop) Supabase no devolvió datos. Eliminación fallida para: {workshop_id}")
                return False
                
            logger.info(f"✅ (delete_workshop) Taller eliminado exitosamente: {workshop_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_workshop) Error inesperado al eliminar taller: {e}", exc_info=True)
            return False
