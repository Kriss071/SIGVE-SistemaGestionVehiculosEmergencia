import logging
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class CatalogService(SigveBaseService):
    """Servicio para gestionar catálogos maestros."""
    
    # ===== Repuestos (Spare Parts) =====
    
    @staticmethod
    def get_all_spare_parts() -> List[Dict[str, Any]]:
        """Obtiene todos los repuestos del catálogo maestro."""
        client = SigveBaseService.get_client()
        query = client.table("spare_part").select("*").order("name")
        return SigveBaseService._execute_query(query, "get_all_spare_parts")
    
    @staticmethod
    def get_spare_part(spare_part_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un repuesto específico."""
        client = SigveBaseService.get_client()
        try:
            result = client.table("spare_part").select("*").eq("id", spare_part_id).maybe_single().execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo repuesto {spare_part_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_spare_part(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo repuesto maestro."""
        client = SigveBaseService.get_client()
        try:
            result = client.table("spare_part").insert(data).execute()
            if result.data:
                logger.info(f"✅ Repuesto creado: {data.get('name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando repuesto: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_spare_part(spare_part_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza un repuesto existente."""
        client = SigveBaseService.get_client()
        try:
            client.table("spare_part").update(data).eq("id", spare_part_id).execute()
            logger.info(f"✅ Repuesto {spare_part_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando repuesto {spare_part_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_spare_part(spare_part_id: int) -> bool:
        """Elimina un repuesto (si no tiene restricciones)."""
        client = SigveBaseService.get_client()
        try:
            client.table("spare_part").delete().eq("id", spare_part_id).execute()
            logger.info(f"🗑️ Repuesto {spare_part_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando repuesto {spare_part_id}: {e}", exc_info=True)
            return False
    
    # ===== Proveedores Globales =====
    
    @staticmethod
    def get_all_global_suppliers() -> List[Dict[str, Any]]:
        """Obtiene todos los proveedores globales (workshop_id = NULL)."""
        client = SigveBaseService.get_client()
        query = client.table("supplier").select("*").is_("workshop_id", "null").order("name")
        return SigveBaseService._execute_query(query, "get_all_global_suppliers")
    
    @staticmethod
    def get_supplier(supplier_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un proveedor específico."""
        client = SigveBaseService.get_client()
        try:
            result = client.table("supplier").select("*").eq("id", supplier_id).maybe_single().execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo proveedor {supplier_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_supplier(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo proveedor."""
        client = SigveBaseService.get_client()
        try:
            result = client.table("supplier").insert(data).execute()
            if result.data:
                logger.info(f"✅ Proveedor creado: {data.get('name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando proveedor: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_supplier(supplier_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza un proveedor existente."""
        client = SigveBaseService.get_client()
        try:
            client.table("supplier").update(data).eq("id", supplier_id).execute()
            logger.info(f"✅ Proveedor {supplier_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor {supplier_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_supplier(supplier_id: int) -> bool:
        """Elimina un proveedor."""
        client = SigveBaseService.get_client()
        try:
            client.table("supplier").delete().eq("id", supplier_id).execute()
            logger.info(f"🗑️ Proveedor {supplier_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando proveedor {supplier_id}: {e}", exc_info=True)
            return False
    
    # ===== Tablas Lookup Genéricas =====
    
    @staticmethod
    def get_catalog_items(table_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los items de una tabla de catálogo.
        
        Args:
            table_name: Nombre de la tabla (vehicle_type, task_type, fuel_type, etc.)
            
        Returns:
            Lista de items del catálogo.
        """
        client = SigveBaseService.get_client()
        query = client.table(table_name).select("*").order("name")
        return SigveBaseService._execute_query(query, f"get_catalog_items({table_name})")
    
    @staticmethod
    def get_catalog_item(table_name: str, item_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un item específico de un catálogo."""
        client = SigveBaseService.get_client()
        try:
            result = client.table(table_name).select("*").eq("id", item_id).maybe_single().execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo item {item_id} de {table_name}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_catalog_item(table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crea un nuevo item en un catálogo."""
        client = SigveBaseService.get_client()
        try:
            result = client.table(table_name).insert(data).execute()
            if result.data:
                logger.info(f"✅ Item creado en {table_name}: {data.get('name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando item en {table_name}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_catalog_item(table_name: str, item_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza un item de un catálogo."""
        client = SigveBaseService.get_client()
        try:
            client.table(table_name).update(data).eq("id", item_id).execute()
            logger.info(f"✅ Item {item_id} actualizado en {table_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando item {item_id} en {table_name}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_catalog_item(table_name: str, item_id: int) -> bool:
        """Elimina un item de un catálogo."""
        client = SigveBaseService.get_client()
        try:
            client.table(table_name).delete().eq("id", item_id).execute()
            logger.info(f"🗑️ Item {item_id} eliminado de {table_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando item {item_id} de {table_name}: {e}", exc_info=True)
            return False


