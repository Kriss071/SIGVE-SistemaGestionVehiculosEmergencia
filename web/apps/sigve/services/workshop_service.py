import logging
from typing import Dict, List, Any, Optional, Tuple
from .base_service import SigveBaseService
from supabase import PostgrestAPIError

logger = logging.getLogger(__name__)


class WorkshopService(SigveBaseService):
    """Servicio para gestionar talleres."""
    
    @staticmethod
    def get_all_workshops() -> List[Dict[str, Any]]:
        """
        Obtiene todos los talleres con información adicional.
        
        Returns:
            Lista de talleres.
        """
        client = SigveBaseService.get_client()
        query = client.table("workshop") \
            .select("*") \
            .order("name")
        
        workshops = SigveBaseService._execute_query(query, "get_all_workshops")
        
        # Contar empleados para cada taller
        for workshop in workshops:
            try:
                employees_count = client.table("user_profile") \
                    .select("id", count="exact") \
                    .eq("workshop_id", workshop['id']) \
                    .execute()
                workshop['employees_count'] = employees_count.count or 0
            except Exception as e:
                logger.error(f"❌ Error contando empleados del taller {workshop['id']}: {e}")
                workshop['employees_count'] = 0
        
        return workshops
    
    @staticmethod
    def get_workshop(workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un taller específico por ID.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Datos del taller o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("workshop") \
                .select("*") \
                .eq("id", workshop_id) \
                .maybe_single() \
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo taller {workshop_id}: {e}", exc_info=True)
            return None
    
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
        
        # Mapeo de campos y sus mensajes de error
        field_mapping = {
            'phone': {
                'keywords': ['phone', 'teléfono', 'telefono'],
                'message': 'Este número de teléfono ya está registrado en otro taller.'
            },
            'email': {
                'keywords': ['email', 'correo', 'e-mail'],
                'message': 'Este correo electrónico ya está registrado en otro taller.'
            },
            'address': {
                'keywords': ['address', 'dirección', 'direccion'],
                'message': 'Esta dirección ya está registrada en otro taller.'
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
            # Los mensajes de PostgreSQL suelen tener el formato: "duplicate key value violates unique constraint \"constraint_name\""
            import re
            constraint_match = re.search(r'unique constraint[^"]*"([^"]+)"', error_details, re.IGNORECASE)
            if constraint_match:
                constraint_name = constraint_match.group(1).lower()
                # Mapear nombres de constraints comunes
                if 'phone' in constraint_name:
                    return {'field': 'phone', 'message': field_mapping['phone']['message']}
                elif 'email' in constraint_name:
                    return {'field': 'email', 'message': field_mapping['email']['message']}
                elif 'address' in constraint_name:
                    return {'field': 'address', 'message': field_mapping['address']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un taller con estos datos. Verifica que el teléfono, correo y dirección sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un taller.
        
        Args:
            data: Datos del taller a verificar.
            exclude_id: ID del taller a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = SigveBaseService.get_client()
        errors = {}
        
        # Verificar teléfono duplicado
        if data.get('phone'):
            query = client.table("workshop").select("id, name").eq("phone", data['phone'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['phone'] = 'Este número de teléfono ya está registrado en otro taller.'
        
        # Verificar email duplicado
        if data.get('email'):
            query = client.table("workshop").select("id, name").eq("email", data['email'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['email'] = 'Este correo electrónico ya está registrado en otro taller.'
        
        # Verificar dirección duplicada
        if data.get('address'):
            query = client.table("workshop").select("id, name").eq("address", data['address'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['address'] = 'Esta dirección ya está registrada en otro taller.'
        
        return errors
    
    @staticmethod
    def create_workshop(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo taller.
        
        Args:
            data: Datos del taller (name, address, phone, email).
            
        Returns:
            Tupla (taller_creado, errores):
            - taller_creado: Datos del taller creado o None si hubo error.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = WorkshopService.check_duplicates(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear taller con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            result = client.table("workshop").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Taller creado: {data.get('name')}")
                return (result.data[0] if isinstance(result.data, list) else result.data, None)
            return None, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando taller: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = WorkshopService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el taller. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error creando taller: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = WorkshopService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el taller. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def update_workshop(workshop_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un taller existente.
        
        Args:
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = WorkshopService.check_duplicates(data, exclude_id=workshop_id)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar taller {workshop_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors
        
        try:
            result = client.table("workshop") \
                .update(data) \
                .eq("id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Taller {workshop_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando taller {workshop_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = WorkshopService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el taller. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error actualizando taller {workshop_id}: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = WorkshopService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el taller. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def delete_workshop(workshop_id: int) -> bool:
        """
        Elimina (desactiva) un taller.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            # En lugar de eliminar, podríamos desactivar usuarios asociados
            # Por ahora, intentamos eliminar directamente
            result = client.table("workshop") \
                .delete() \
                .eq("id", workshop_id) \
                .execute()
            
            logger.info(f"🗑️ Taller {workshop_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando taller {workshop_id}: {e}", exc_info=True)
            return False


