import logging
from typing import Dict, List, Any, Optional, Tuple
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
    def _parse_duplicate_error(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado en proveedores.
        
        Args:
            error: La excepción capturada.
            
        Returns:
            Diccionario con el campo duplicado y mensaje, o None si no es un error de duplicación.
        """
        error_msg = str(error).lower()
        error_details = getattr(error, 'message', '') or error_msg
        
        # Mapeo de campos y sus mensajes de error
        field_mapping = {
            'name': {
                'keywords': ['name', 'nombre'],
                'message': 'Este nombre de proveedor ya está registrado.'
            },
            'rut': {
                'keywords': ['rut'],
                'message': 'Este RUT ya está registrado en otro proveedor.'
            },
            'phone': {
                'keywords': ['phone', 'teléfono', 'telefono'],
                'message': 'Este número de teléfono ya está registrado en otro proveedor.'
            },
            'email': {
                'keywords': ['email', 'correo', 'e-mail'],
                'message': 'Este correo electrónico ya está registrado en otro proveedor.'
            }
        }
        
        # Buscar el campo duplicado en el mensaje de error
        for field, info in field_mapping.items():
            for keyword in info['keywords']:
                if keyword in error_details.lower():
                    return {
                        'field': field,
                        'message': info['message']
                    }
        
        # Si no se identifica un campo específico, verificar si es un error de constraint único
        if 'unique constraint' in error_details or 'duplicate key' in error_details or '23505' in error_details:
            return {
                'field': 'general',
                'message': 'Ya existe un registro con estos datos. Verifica que los datos sean únicos.'
            }
        
        return None
    
    @staticmethod
    def create_supplier(workshop_id: int, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo proveedor local del taller.
        
        Args:
            workshop_id: ID del taller.
            data: Datos del proveedor (name, rut, address, phone, email).
            
        Returns:
            Tupla (proveedor_creado, errores). Si hay errores, el primer elemento es None.
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
                supplier = result.data[0] if isinstance(result.data, list) else result.data
                return supplier, None
            return None, {'general': ['Error al crear el proveedor.']}
        except Exception as e:
            logger.error(f"❌ Error creando proveedor: {e}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = SupplierService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: [duplicate_error['message']]}
            
            # Error genérico
            error_msg = str(e)
            if 'duplicate key value violates unique constraint' in error_msg or '23505' in error_msg:
                duplicate_error = SupplierService._parse_duplicate_error(e)
                if duplicate_error:
                    return None, {duplicate_error['field']: [duplicate_error['message']]}
            
            return None, {'general': ['Error al crear el proveedor. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def update_supplier(supplier_id: int, workshop_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un proveedor local del taller.
        
        Args:
            supplier_id: ID del proveedor.
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores). Si hay errores, el primer elemento es False.
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
            return True, None
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor {supplier_id}: {e}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = SupplierService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            # Error genérico
            error_msg = str(e)
            if 'duplicate key value violates unique constraint' in error_msg or '23505' in error_msg:
                duplicate_error = SupplierService._parse_duplicate_error(e)
                if duplicate_error:
                    return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            return False, {'general': ['Error al actualizar el proveedor. Por favor, intenta nuevamente.']}
    
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


