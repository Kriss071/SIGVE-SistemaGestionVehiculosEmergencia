import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from .base_service import WorkshopBaseService
from supabase import PostgrestAPIError

logger = logging.getLogger(__name__)


class InventoryService(WorkshopBaseService):
    """Servicio para gestionar el inventario del taller."""
    
    @staticmethod
    def _convert_decimal_to_float(value: Any) -> Any:
        """
        Convierte un valor Decimal a float para serialización JSON.
        
        Args:
            value: Valor que puede ser Decimal, float, int, etc.
            
        Returns:
            float si era Decimal, el valor original en caso contrario.
        """
        if isinstance(value, Decimal):
            return float(value)
        return value
    
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
    def check_duplicate_workshop_sku(workshop_id: int, workshop_sku: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si un workshop_sku ya está en uso en el taller.
        
        Args:
            workshop_id: ID del taller.
            workshop_sku: SKU interno a verificar.
            exclude_id: ID del item a excluir de la verificación (para edición).
            
        Returns:
            True si el SKU está duplicado, False si está disponible.
        """
        if not workshop_sku or not workshop_sku.strip():
            return False
        
        client = WorkshopBaseService.get_client()
        query = client.table("workshop_inventory").select("id").eq("workshop_id", workshop_id).eq("workshop_sku", workshop_sku.strip())
        
        if exclude_id:
            query = query.neq("id", exclude_id)
        
        result = query.execute()
        return result.data and len(result.data) > 0
    
    @staticmethod
    def _parse_duplicate_error(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado.
        
        Args:
            error: La excepción capturada.
            
        Returns:
            Diccionario con el campo duplicado y mensaje, o None si no es un error de duplicación.
        """
        error_msg = str(error).lower()
        error_details = getattr(error, 'message', '') or error_msg
        
        # Verificar si es un error de constraint único
        if 'unique constraint' in error_details or 'duplicate key' in error_details or '23505' in error_details:
            # Buscar workshop_sku en el mensaje
            if 'workshop_sku' in error_details:
                return {
                    'field': 'workshop_sku',
                    'message': 'Este SKU interno ya está registrado en otro repuesto del inventario.'
                }
            
            # Error genérico de duplicación
            return {
                'field': 'general',
                'message': 'Ya existe un registro con estos datos. Verifica que el SKU interno sea único.'
            }
        
        return None
    
    @staticmethod
    def add_to_inventory(workshop_id: int, user_id: str, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Agrega un repuesto al inventario del taller o actualiza si ya existe.
        
        Args:
            workshop_id: ID del taller.
            user_id: ID del usuario que realiza la operación.
            data: Datos del repuesto (spare_part_id, quantity, current_cost, supplier_id, etc).
            
        Returns:
            Tupla (item_creado/actualizado, errores):
            - item_creado: Datos del item creado/actualizado o None si hubo error.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = WorkshopBaseService.get_client()
        
        spare_part_id = data['spare_part_id']
        workshop_sku = data.get('workshop_sku')
        
        # Verificar duplicados de workshop_sku antes de intentar crear/actualizar
        if workshop_sku and workshop_sku.strip():
            if InventoryService.check_duplicate_workshop_sku(workshop_id, workshop_sku):
                logger.warning(f"⚠️ Intento de agregar repuesto con SKU interno duplicado: {workshop_sku}")
                return None, {'workshop_sku': 'Este SKU interno ya está registrado en otro repuesto del inventario.'}
        
        try:
            # Verificar si el repuesto ya existe en el inventario
            existing = client.table("workshop_inventory") \
                .select("id, quantity") \
                .eq("workshop_id", workshop_id) \
                .eq("spare_part_id", spare_part_id) \
                .maybe_single() \
                .execute()
            
            logger.debug(f"🔍 Verificando existencia: workshop_id={workshop_id}, spare_part_id={spare_part_id}, existing={existing}")
            
            # Verificar si existe un registro (existing puede ser None o existing.data puede ser None)
            if existing and existing.data:
                # Verificar duplicados de workshop_sku excluyendo el item actual
                if workshop_sku and workshop_sku.strip():
                    if InventoryService.check_duplicate_workshop_sku(workshop_id, workshop_sku, exclude_id=existing.data['id']):
                        logger.warning(f"⚠️ Intento de actualizar repuesto con SKU interno duplicado: {workshop_sku}")
                        return None, {'workshop_sku': 'Este SKU interno ya está registrado en otro repuesto del inventario.'}
                
                # Actualizar cantidad existente (sumar a la existente)
                new_quantity = existing.data['quantity'] + data.get('quantity', 0)
                current_cost = InventoryService._convert_decimal_to_float(data.get('current_cost'))
                update_data = {
                    'quantity': new_quantity,
                    'current_cost': current_cost,
                    'last_updated_by_user_id': user_id,
                    'updated_at': 'now()'
                }
                
                # Solo actualizar campos opcionales si se proporcionan valores
                if 'supplier_id' in data and data.get('supplier_id') is not None:
                    update_data['supplier_id'] = data['supplier_id']
                if 'location' in data and data.get('location') is not None:
                    update_data['location'] = data['location']
                if 'workshop_sku' in data and data.get('workshop_sku') is not None:
                    update_data['workshop_sku'] = data['workshop_sku'].strip() if data['workshop_sku'] else None
                
                result = client.table("workshop_inventory") \
                    .update(update_data) \
                    .eq("id", existing.data['id']) \
                    .execute()
                
                logger.info(f"✅ Inventario actualizado: {existing.data['id']}")
                return (result.data[0] if result.data else None, None)
            else:
                # Crear nuevo registro
                current_cost = InventoryService._convert_decimal_to_float(data.get('current_cost', 0))
                inventory_data = {
                    'workshop_id': workshop_id,
                    'spare_part_id': spare_part_id,
                    'quantity': data.get('quantity', 0),
                    'current_cost': current_cost,
                    'supplier_id': data.get('supplier_id'),
                    'location': data.get('location'),
                    'workshop_sku': workshop_sku.strip() if workshop_sku else None,
                    'last_updated_by_user_id': user_id
                }
                
                logger.debug(f"➕ Creando nuevo registro de inventario: {inventory_data}")
                
                result = client.table("workshop_inventory").insert(inventory_data).execute()
                
                if result.data:
                    logger.info(f"✅ Repuesto agregado al inventario")
                    return (result.data[0] if isinstance(result.data, list) else result.data, None)
                return None, None
                
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API agregando repuesto al inventario: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = InventoryService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': 'Error al agregar el repuesto. Por favor, intenta nuevamente.'}
        except Exception as e:
            error_msg = str(e)
            # Detectar error de clave duplicada
            if 'duplicate key value violates unique constraint' in error_msg or '23505' in error_msg:
                logger.error(f"❌ Error de clave duplicada al agregar repuesto. Error: {error_msg}")
                # Intentar parsear el error de duplicación
                duplicate_error = InventoryService._parse_duplicate_error(e)
                if duplicate_error:
                    return None, {duplicate_error['field']: duplicate_error['message']}
                return None, {'general': 'Ya existe un registro con estos datos. Verifica que el SKU interno sea único.'}
            else:
                logger.error(f"❌ Error agregando repuesto al inventario: {error_msg}", exc_info=True)
                return None, {'general': 'Error al agregar el repuesto. Por favor, intenta nuevamente.'}
    
    @staticmethod
    def update_inventory(inventory_id: int, workshop_id: int, user_id: str, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un item del inventario (ajuste de stock o costo).
        
        Args:
            inventory_id: ID del item.
            workshop_id: ID del taller.
            user_id: ID del usuario.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = WorkshopBaseService.get_client()
        
        workshop_sku = data.get('workshop_sku')
        
        # Verificar duplicados de workshop_sku antes de intentar actualizar
        if workshop_sku and workshop_sku.strip():
            if InventoryService.check_duplicate_workshop_sku(workshop_id, workshop_sku, exclude_id=inventory_id):
                logger.warning(f"⚠️ Intento de actualizar inventario {inventory_id} con SKU interno duplicado: {workshop_sku}")
                return False, {'workshop_sku': 'Este SKU interno ya está registrado en otro repuesto del inventario.'}
        
        try:
            update_data = {
                'last_updated_by_user_id': user_id,
                'updated_at': 'now()'
            }
            
            # Agregar solo los campos que se proporcionaron
            if 'quantity' in data:
                update_data['quantity'] = data['quantity']
            if 'current_cost' in data:
                update_data['current_cost'] = InventoryService._convert_decimal_to_float(data['current_cost'])
            # Para campos opcionales, incluir incluso si son None (para poder limpiarlos)
            if 'supplier_id' in data:
                update_data['supplier_id'] = data['supplier_id']
            if 'location' in data:
                update_data['location'] = data['location']
            if 'workshop_sku' in data:
                update_data['workshop_sku'] = data['workshop_sku'].strip() if data['workshop_sku'] else None
            
            result = client.table("workshop_inventory") \
                .update(update_data) \
                .eq("id", inventory_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Inventario {inventory_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando inventario {inventory_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = InventoryService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': 'Error al actualizar el inventario. Por favor, intenta nuevamente.'}
        except Exception as e:
            error_msg = str(e)
            # Detectar error de clave duplicada
            if 'duplicate key value violates unique constraint' in error_msg or '23505' in error_msg:
                logger.error(f"❌ Error de clave duplicada al actualizar inventario {inventory_id}. Error: {error_msg}")
                # Intentar parsear el error de duplicación
                duplicate_error = InventoryService._parse_duplicate_error(e)
                if duplicate_error:
                    return False, {duplicate_error['field']: duplicate_error['message']}
                return False, {'general': 'Ya existe un registro con estos datos. Verifica que el SKU interno sea único.'}
            else:
                logger.error(f"❌ Error actualizando inventario {inventory_id}: {e}", exc_info=True)
                return False, {'general': 'Error al actualizar el inventario. Por favor, intenta nuevamente.'}
    
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
    def search_spare_parts(search_term: str = None, limit: int = None):
        """
        Busca repuestos en el catálogo maestro.
        
        Args:
            search_term: Término de búsqueda (nombre, SKU o marca).
            limit: Límite de resultados (opcional, para mejorar rendimiento).
            
        Returns:
            Lista de repuestos que coinciden.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("spare_part").select("*").order("name")
        
        # Aplicar límite si se especifica
        if limit:
            query = query.limit(limit)
        
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


