import logging
from typing import Dict, List, Any, Optional
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class SupplierService(WorkshopBaseService):
    """Servicio para gestionar proveedores del taller."""
    
    @staticmethod
    def get_all_suppliers(workshop_id: int):
        """
        Obtiene todos los proveedores disponibles para el taller (globales + locales).
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Lista de proveedores.
        """
        client = WorkshopBaseService.get_client()
        
        # Obtener proveedores globales (workshop_id es NULL) y locales del taller
        try:
            # Proveedores globales
            global_suppliers = client.table("supplier") \
                .select("*, workshop:workshop_id(name)") \
                .is_("workshop_id", "null") \
                .order("name") \
                .execute()
            
            # Proveedores locales del taller
            local_suppliers = client.table("supplier") \
                .select("*, workshop:workshop_id(name)") \
                .eq("workshop_id", workshop_id) \
                .order("name") \
                .execute()
            
            # Combinar ambas listas
            all_suppliers = []
            if global_suppliers.data:
                for supplier in global_suppliers.data:
                    supplier['is_global'] = True
                    all_suppliers.append(supplier)
            
            if local_suppliers.data:
                for supplier in local_suppliers.data:
                    supplier['is_global'] = False
                    all_suppliers.append(supplier)
            
            return all_suppliers
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo proveedores: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_supplier(supplier_id: int, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un proveedor específico (solo si es global o pertenece al taller).
        
        Args:
            supplier_id: ID del proveedor.
            workshop_id: ID del taller.
            
        Returns:
            Datos del proveedor o None.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Buscar proveedor que sea global o del taller
            result = client.table("supplier") \
                .select("*") \
                .eq("id", supplier_id) \
                .execute()
            
            if not result.data:
                return None
            
            supplier = result.data[0]
            supplier_workshop_id = supplier.get('workshop_id')
            
            # Verificar que sea global o del taller actual
            if supplier_workshop_id is None or supplier_workshop_id == workshop_id:
                return supplier
            else:
                logger.warning(f"⚠️ Intento de acceso a proveedor {supplier_id} de otro taller")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo proveedor {supplier_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def create_supplier(workshop_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo proveedor local del taller.
        
        Args:
            workshop_id: ID del taller.
            data: Datos del proveedor (name, rut, address, phone, email).
            
        Returns:
            Datos del proveedor creado o None.
        """
        client = WorkshopBaseService.get_client()
        
        supplier_data = {
            'workshop_id': workshop_id,
            'name': data['name'],
            'rut': data.get('rut'),
            'address': data.get('address'),
            'phone': data.get('phone'),
            'email': data.get('email')
        }
        
        try:
            result = client.table("supplier").insert(supplier_data).execute()
            
            if result.data:
                logger.info(f"✅ Proveedor local creado: {data['name']}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando proveedor: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_supplier(supplier_id: int, workshop_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un proveedor local del taller.
        
        Args:
            supplier_id: ID del proveedor.
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Solo permitir actualizar proveedores locales del taller
            result = client.table("supplier") \
                .update(data) \
                .eq("id", supplier_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Proveedor {supplier_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor {supplier_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def delete_supplier(supplier_id: int, workshop_id: int) -> bool:
        """
        Elimina un proveedor local del taller.
        
        Args:
            supplier_id: ID del proveedor.
            workshop_id: ID del taller.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Solo permitir eliminar proveedores locales del taller
            result = client.table("supplier") \
                .delete() \
                .eq("id", supplier_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"🗑️ Proveedor {supplier_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando proveedor {supplier_id}: {e}", exc_info=True)
            return False


