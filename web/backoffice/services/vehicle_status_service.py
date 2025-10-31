import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class VehicleStatusService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Estados de Vehículo (tabla 'vehicle_status').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "vehicle_status"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de VehicleStatusService creada para la tabla '{self.TABLE_NAME}'.")

    def list_vehicle_statuses(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los estados de vehículo, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un estado de vehículo.
        """
        logger.info(f"📄 (list_vehicle_statuses) Obteniendo lista de {self.TABLE_NAME}s...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_vehicle_statuses")

    def get_vehicle_status(self, vehicle_status_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un estado de vehículo específico por su ID.
        
        Args:
            vehicle_status_id: El ID (int) del estado de vehículo.
            
        Returns:
            Un diccionario con los datos del estado de vehículo o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_vehicle_status) Obteniendo {self.TABLE_NAME} con ID: {vehicle_status_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", vehicle_status_id).maybe_single()
        
        result = self._execute_query(query, "get_vehicle_status")
        
        if not result:
            logger.warning(f"⚠️ (get_vehicle_status) {self.TABLE_NAME} no encontrado: {vehicle_status_id}")
            return None
            
        logger.info(f"✅ (get_vehicle_status) {self.TABLE_NAME} encontrado: {vehicle_status_id}")
        return result

    def create_vehicle_status(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de estado de vehículo.
        
        Args:
            data: Diccionario con los datos (name, description) del estado de vehículo.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_vehicle_status) Intentando crear {self.TABLE_NAME}: {data.get('name')}")
        try:
            data.pop('id', None)
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_vehicle_status) Supabase no devolvió datos.")
                return False
                
            logger.info(f"✅ (create_vehicle_status) {self.TABLE_NAME} creado: {response.data[0].get('id')}")
            return True
        except Exception as e:
            logger.error(f"❌ (create_vehicle_status) Error inesperado: {e}", exc_info=True)
            return False

    def update_vehicle_status(self, vehicle_status_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de estado de vehículo existente.
        
        Args:
            vehicle_status_id: El ID del estado de vehículo a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_vehicle_status) Intentando actualizar {self.TABLE_NAME}: {vehicle_status_id}")
        data.pop('id', None)
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", vehicle_status_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_vehicle_status) Actualización fallida: {vehicle_status_id}")
                return False
                
            logger.info(f"✅ (update_vehicle_status) {self.TABLE_NAME} actualizado: {vehicle_status_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_vehicle_status) Error inesperado: {e}", exc_info=True)
            return False

    def delete_vehicle_status(self, vehicle_status_id: int) -> bool:
        """
        Elimina un registro de estado de vehículo.
        
        Args:
            vehicle_status_id: El ID del estado de vehículo a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_vehicle_status) Intentando eliminar {self.TABLE_NAME}: {vehicle_status_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", vehicle_status_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_vehicle_status) Eliminación fallida: {vehicle_status_id}")
                return False
                
            logger.info(f"✅ (delete_vehicle_status) {self.TABLE_NAME} eliminado: {vehicle_status_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_vehicle_status) Error inesperado: {e}", exc_info=True)
            return False