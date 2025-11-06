import logging
from typing import Dict, List, Any, Optional
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class InventoryService(WorkshopBaseService):
    """Servicio para gestionar el inventario del taller."""
    
    @staticmethod
    def get_all_inventory(workshop_id: int):
        """
        Obtiene todo el inventario de un taller.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Lista de items del inventario con información del repuesto maestro.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("workshop_inventory") \
            .select("""
                id,
                quantity,
                current_cost,
                location,
                workshop_sku,
                updated_at,
                spare_part:spare_part_id(id, name, sku, brand, description),
                supplier:supplier_id(id, name)
            """) \
            .eq("workshop_id", workshop_id) \
            .order("spare_part_id")
        
        return WorkshopBaseService._execute_query(query, "get_all_inventory")
    
    @staticmethod
    def get_inventory_item(inventory_id: int, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un item específico del inventario.
        
        Args:
            inventory_id: ID del item en el inventario.
            workshop_id: ID del taller.
            
        Returns:
            Datos del item o None.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("workshop_inventory") \
            .select("""
                *,
                spare_part:spare_part_id(*),
                supplier:supplier_id(*)
            """) \
            .eq("id", inventory_id) \
            .eq("workshop_id", workshop_id)
        
        return WorkshopBaseService._execute_single(query, "get_inventory_item")
    
    @staticmethod
    def add_to_inventory(workshop_id: int, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Agrega un repuesto al inventario del taller o actualiza si ya existe.
        
        Args:
            workshop_id: ID del taller.
            user_id: ID del usuario que realiza la operación.
            data: Datos del repuesto (spare_part_id, quantity, current_cost, supplier_id, etc).
            
        Returns:
            Datos del item creado/actualizado o None.
        """
        client = WorkshopBaseService.get_client()
        
        spare_part_id = data['spare_part_id']
        
        try:
            # Verificar si el repuesto ya existe en el inventario
            existing = client.table("workshop_inventory") \
                .select("id, quantity") \
                .eq("workshop_id", workshop_id) \
                .eq("spare_part_id", spare_part_id) \
                .maybe_single() \
                .execute()
            
            if existing.data:
                # Actualizar cantidad existente
                new_quantity = existing.data['quantity'] + data.get('quantity', 0)
                update_data = {
                    'quantity': new_quantity,
                    'current_cost': data.get('current_cost'),
                    'supplier_id': data.get('supplier_id'),
                    'location': data.get('location'),
                    'workshop_sku': data.get('workshop_sku'),
                    'last_updated_by_user_id': user_id,
                    'updated_at': 'now()'
                }
                
                result = client.table("workshop_inventory") \
                    .update(update_data) \
                    .eq("id", existing.data['id']) \
                    .execute()
                
                logger.info(f"✅ Inventario actualizado: {existing.data['id']}")
                return result.data[0] if result.data else None
            else:
                # Crear nuevo registro
                inventory_data = {
                    'workshop_id': workshop_id,
                    'spare_part_id': spare_part_id,
                    'quantity': data.get('quantity', 0),
                    'current_cost': data.get('current_cost', 0),
                    'supplier_id': data.get('supplier_id'),
                    'location': data.get('location'),
                    'workshop_sku': data.get('workshop_sku'),
                    'last_updated_by_user_id': user_id
                }
                
                result = client.table("workshop_inventory").insert(inventory_data).execute()
                
                if result.data:
                    logger.info(f"✅ Repuesto agregado al inventario")
                    return result.data[0] if isinstance(result.data, list) else result.data
                return None
                
        except Exception as e:
            logger.error(f"❌ Error agregando repuesto al inventario: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_inventory(inventory_id: int, workshop_id: int, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Actualiza un item del inventario (ajuste de stock o costo).
        
        Args:
            inventory_id: ID del item.
            workshop_id: ID del taller.
            user_id: ID del usuario.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            update_data = {
                'last_updated_by_user_id': user_id,
                'updated_at': 'now()'
            }
            
            # Agregar solo los campos que se proporcionaron
            if 'quantity' in data:
                update_data['quantity'] = data['quantity']
            if 'current_cost' in data:
                update_data['current_cost'] = data['current_cost']
            if 'supplier_id' in data:
                update_data['supplier_id'] = data['supplier_id']
            if 'location' in data:
                update_data['location'] = data['location']
            if 'workshop_sku' in data:
                update_data['workshop_sku'] = data['workshop_sku']
            
            result = client.table("workshop_inventory") \
                .update(update_data) \
                .eq("id", inventory_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Inventario {inventory_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando inventario {inventory_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_from_inventory(inventory_id: int, workshop_id: int) -> bool:
        """
        Elimina un repuesto del inventario del taller.
        
        Args:
            inventory_id: ID del item.
            workshop_id: ID del taller.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            result = client.table("workshop_inventory") \
                .delete() \
                .eq("id", inventory_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"🗑️ Item {inventory_id} eliminado del inventario")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando item {inventory_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def search_spare_parts(search_term: str = None):
        """
        Busca repuestos en el catálogo maestro.
        
        Args:
            search_term: Término de búsqueda (nombre, SKU o marca).
            
        Returns:
            Lista de repuestos que coinciden.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("spare_part").select("*").order("name")
        
        # Si hay término de búsqueda, filtrar
        if search_term:
            # Nota: Supabase no soporta OR en múltiples campos directamente
            # Necesitamos hacer la búsqueda en Python o usar RPC
            all_parts = WorkshopBaseService._execute_query(query, "search_spare_parts")
            search_lower = search_term.lower()
            
            filtered = [
                part for part in all_parts
                if (search_lower in part.get('name', '').lower() or
                    search_lower in part.get('sku', '').lower() or
                    search_lower in part.get('brand', '').lower())
            ]
            return filtered
        else:
            return WorkshopBaseService._execute_query(query, "search_spare_parts")


