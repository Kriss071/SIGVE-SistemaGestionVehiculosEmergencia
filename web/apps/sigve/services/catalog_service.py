import logging
from typing import Dict, List, Any, Optional, Tuple
from .base_service import SigveBaseService
from supabase import PostgrestAPIError

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
    def _parse_duplicate_error_spare_part(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado en repuestos.
        
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
                'message': 'Este nombre de repuesto ya está registrado.'
            },
            'sku': {
                'keywords': ['sku', 'código', 'codigo'],
                'message': 'Este SKU ya está registrado en otro repuesto.'
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
            # Intentar extraer el nombre del constraint del mensaje
            import re
            constraint_match = re.search(r'unique constraint[^"]*"([^"]+)"', error_details, re.IGNORECASE)
            if constraint_match:
                constraint_name = constraint_match.group(1).lower()
                # Mapear nombres de constraints comunes
                if 'name' in constraint_name:
                    return {'field': 'name', 'message': field_mapping['name']['message']}
                elif 'sku' in constraint_name:
                    return {'field': 'sku', 'message': field_mapping['sku']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un repuesto con estos datos. Verifica que el nombre y SKU sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates_spare_part(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un repuesto.
        
        Args:
            data: Datos del repuesto a verificar.
            exclude_id: ID del repuesto a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = SigveBaseService.get_client()
        errors = {}
        
        # Verificar nombre duplicado
        if data.get('name'):
            query = client.table("spare_part").select("id, name").eq("name", data['name'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['name'] = 'Este nombre de repuesto ya está registrado.'
        
        # Verificar SKU duplicado
        if data.get('sku'):
            query = client.table("spare_part").select("id, name").eq("sku", data['sku'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['sku'] = 'Este SKU ya está registrado en otro repuesto.'
        
        return errors
    
    @staticmethod
    def create_spare_part(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo repuesto maestro.
        
        Args:
            data: Datos del repuesto (name, sku, brand, description).
            
        Returns:
            Tupla (repuesto_creado, errores):
            - repuesto_creado: Datos del repuesto creado o None si hubo error.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = CatalogService.check_duplicates_spare_part(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear repuesto con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            result = client.table("spare_part").insert(data).execute()
            if result.data:
                logger.info(f"✅ Repuesto creado: {data.get('name')}")
                return (result.data[0] if isinstance(result.data, list) else result.data, None)
            return None, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando repuesto: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_spare_part(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el repuesto. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error creando repuesto: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_spare_part(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el repuesto. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def update_spare_part(spare_part_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un repuesto existente.
        
        Args:
            spare_part_id: ID del repuesto.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = CatalogService.check_duplicates_spare_part(data, exclude_id=spare_part_id)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar repuesto {spare_part_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors
        
        try:
            client.table("spare_part").update(data).eq("id", spare_part_id).execute()
            logger.info(f"✅ Repuesto {spare_part_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando repuesto {spare_part_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_spare_part(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el repuesto. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error actualizando repuesto {spare_part_id}: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_spare_part(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el repuesto. Por favor, intenta nuevamente.']}
    
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
    def _parse_duplicate_error_supplier(error: Exception) -> Optional[Dict[str, str]]:
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
            # Intentar extraer el nombre del constraint del mensaje
            import re
            constraint_match = re.search(r'unique constraint[^"]*"([^"]+)"', error_details, re.IGNORECASE)
            if constraint_match:
                constraint_name = constraint_match.group(1).lower()
                # Mapear nombres de constraints comunes
                if 'name' in constraint_name:
                    return {'field': 'name', 'message': field_mapping['name']['message']}
                elif 'rut' in constraint_name:
                    return {'field': 'rut', 'message': field_mapping['rut']['message']}
                elif 'phone' in constraint_name:
                    return {'field': 'phone', 'message': field_mapping['phone']['message']}
                elif 'email' in constraint_name:
                    return {'field': 'email', 'message': field_mapping['email']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un proveedor con estos datos. Verifica que el nombre, RUT, teléfono y correo sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates_supplier(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un proveedor.
        
        Args:
            data: Datos del proveedor a verificar.
            exclude_id: ID del proveedor a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = SigveBaseService.get_client()
        errors = {}
        
        # Verificar nombre duplicado
        if data.get('name'):
            query = client.table("supplier").select("id, name").eq("name", data['name'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['name'] = 'Este nombre de proveedor ya está registrado.'
        
        # Verificar RUT duplicado (solo si se proporciona)
        if data.get('rut'):
            query = client.table("supplier").select("id, name").eq("rut", data['rut'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['rut'] = 'Este RUT ya está registrado en otro proveedor.'
        
        # Verificar teléfono duplicado (solo si se proporciona)
        if data.get('phone'):
            query = client.table("supplier").select("id, name").eq("phone", data['phone'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['phone'] = 'Este número de teléfono ya está registrado en otro proveedor.'
        
        # Verificar email duplicado (solo si se proporciona)
        if data.get('email'):
            query = client.table("supplier").select("id, name").eq("email", data['email'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['email'] = 'Este correo electrónico ya está registrado en otro proveedor.'
        
        return errors
    
    @staticmethod
    def create_supplier(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo proveedor.
        
        Args:
            data: Datos del proveedor (name, rut, address, phone, email).
            
        Returns:
            Tupla (proveedor_creado, errores):
            - proveedor_creado: Datos del proveedor creado o None si hubo error.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = CatalogService.check_duplicates_supplier(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear proveedor con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            result = client.table("supplier").insert(data).execute()
            if result.data:
                logger.info(f"✅ Proveedor creado: {data.get('name')}")
                return (result.data[0] if isinstance(result.data, list) else result.data, None)
            return None, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando proveedor: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_supplier(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el proveedor. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error creando proveedor: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_supplier(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el proveedor. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def update_supplier(supplier_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un proveedor existente.
        
        Args:
            supplier_id: ID del proveedor.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = CatalogService.check_duplicates_supplier(data, exclude_id=supplier_id)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar proveedor {supplier_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors
        
        try:
            client.table("supplier").update(data).eq("id", supplier_id).execute()
            logger.info(f"✅ Proveedor {supplier_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando proveedor {supplier_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_supplier(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el proveedor. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error actualizando proveedor {supplier_id}: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = CatalogService._parse_duplicate_error_supplier(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el proveedor. Por favor, intenta nuevamente.']}
    
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


