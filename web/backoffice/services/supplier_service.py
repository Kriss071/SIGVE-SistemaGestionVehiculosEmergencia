import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class SupplierService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Proveedores (tabla 'supplier').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "supplier"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de SupplierService creada para la tabla '{self.TABLE_NAME}'.")

    def list_suppliers(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los proveedores, ordenados por nombre.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un proveedor.
        """
        logger.info(f"📄 (list_suppliers) Obteniendo lista de proveedores...")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_suppliers")

    def get_supplier(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un proveedor específico por su ID.
        
        Args:
            supplier_id: El ID (int) del proveedor.
            
        Returns:
            Un diccionario con los datos del proveedor o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_supplier) Obteniendo proveedor con ID: {supplier_id}")
        query = self.client.table(self.TABLE_NAME).select("*").eq("id", supplier_id).maybe_single()
        
        result = self._execute_query(query, "get_supplier")
        
        if not result:
            logger.warning(f"⚠️ (get_supplier) Proveedor no encontrado: {supplier_id}")
            return None
            
        logger.info(f"✅ (get_supplier) Proveedor encontrado: {supplier_id}")
        return result

    def create_supplier(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de proveedor.
        
        Args:
            data: Diccionario con los datos del proveedor a crear.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_supplier) Intentando crear proveedor con nombre: {data.get('name')}")
        try:
            data.pop('id', None) # Asegurarse de que el ID no esté en el insert
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_supplier) Supabase no devolvió datos. Creación fallida.")
                return False
                
            logger.info(f"✅ (create_supplier) Proveedor creado exitosamente: {response.data[0].get('id')}")
            return True
        except PostgrestAPIError as e:
            logger.error(f"❌ (create_supplier) Error de API al crear proveedor: {e.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ (create_supplier) Error inesperado al crear proveedor: {e}", exc_info=True)
            return False

    def update_supplier(self, supplier_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de proveedor existente.
        
        Args:
            supplier_id: El ID del proveedor a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_supplier) Intentando actualizar proveedor: {supplier_id}")
        data.pop('id', None) # Asegurarse de no intentar actualizar la 'id'
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", supplier_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_supplier) Supabase no devolvió datos. Actualización fallida para: {supplier_id}")
                return False
                
            logger.info(f"✅ (update_supplier) Proveedor actualizado exitosamente: {supplier_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_supplier) Error inesperado al actualizar proveedor: {e}", exc_info=True)
            return False

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        Elimina un registro de proveedor.
        
        Args:
            supplier_id: El ID del proveedor a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_supplier) Intentando eliminar proveedor: {supplier_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", supplier_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_supplier) Supabase no devolvió datos. Eliminación fallida para: {supplier_id}")
                return False
                
            logger.info(f"✅ (delete_supplier) Proveedor eliminado exitosamente: {supplier_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_supplier) Error inesperado al eliminar proveedor: {e}", exc_info=True)
            return False
