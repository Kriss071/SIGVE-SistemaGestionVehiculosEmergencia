import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class RequestTypeService(SigveBaseService):
    """
    Servicio para gestionar los tipos de solicitudes (request_type).
    Los tipos de solicitudes definen qué campos se deben llenar en un formulario.
    """
    
    @staticmethod
    def get_all_request_types() -> List[Dict[str, Any]]:
        """
        Obtiene todos los tipos de solicitudes.
        
        Returns:
            Lista de tipos de solicitudes con su esquema de formulario.
        """
        client = SigveBaseService.get_client()
        
        query = client.table('request_type').select('*').order('name')
        
        return SigveBaseService._execute_query(query, 'get_all_request_types')
    
    @staticmethod
    def get_request_type(request_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un tipo de solicitud por su ID.
        
        Args:
            request_type_id: ID del tipo de solicitud.
            
        Returns:
            Diccionario con los datos del tipo de solicitud o None.
        """
        client = SigveBaseService.get_client()
        
        query = client.table('request_type').select('*').eq('id', request_type_id)
        
        return SigveBaseService._execute_single(query, 'get_request_type')
    
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
            'name': {
                'keywords': ['name', 'nombre'],
                'message': 'Este nombre de tipo de solicitud ya está registrado.'
            },
            'target_table': {
                'keywords': ['target_table', 'tabla objetivo'],
                'message': 'Esta tabla objetivo ya está registrada en otro tipo de solicitud.'
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
            constraint_match = re.search(r'unique constraint[^"]*"([^"]+)"', error_details, re.IGNORECASE)
            if constraint_match:
                constraint_name = constraint_match.group(1).lower()
                # Mapear nombres de constraints comunes
                if 'name' in constraint_name:
                    return {'field': 'name', 'message': field_mapping['name']['message']}
                elif 'target_table' in constraint_name or 'target' in constraint_name:
                    return {'field': 'target_table', 'message': field_mapping['target_table']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un tipo de solicitud con estos datos. Verifica que el nombre y tabla objetivo sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un tipo de solicitud.
        
        Args:
            data: Datos del tipo de solicitud a verificar.
            exclude_id: ID del tipo de solicitud a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = SigveBaseService.get_client()
        errors = {}
        
        # Verificar nombre duplicado
        if data.get('name'):
            query = client.table("request_type").select("id, name").eq("name", data['name'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            
            if existing.data and len(existing.data) > 0:
                errors['name'] = 'Este nombre de tipo de solicitud ya está registrado.'
        
        # Verificar target_table duplicado
        if data.get('target_table'):
            query = client.table("request_type").select("id, target_table").eq("target_table", data['target_table'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            
            if existing.data and len(existing.data) > 0:
                errors['target_table'] = 'Esta tabla objetivo ya está registrada en otro tipo de solicitud.'
        
        return errors
    
    @staticmethod
    def create_request_type(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
        """
        Crea un nuevo tipo de solicitud.
        
        Args:
            data: Diccionario con los campos:
                - name: Nombre del tipo de solicitud
                - description: Descripción (opcional)
                - target_table: Tabla objetivo donde se guardará la data
                - form_schema: JSONB con el esquema del formulario
                
        Returns:
            Tupla (tipo_solicitud_creado, errores). 
            Si hay errores, el primer elemento es None y el segundo contiene los errores por campo.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = RequestTypeService.check_duplicates(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear tipo de solicitud con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            response = client.table('request_type').insert(data).execute()
            logger.info(f"✅ Tipo de solicitud '{data['name']}' creado correctamente.")
            return response.data[0] if response.data else None, {}
        except Exception as e:
            logger.error(f"❌ Error al crear tipo de solicitud: {e}", exc_info=True)
            # Intentar parsear error de duplicado
            duplicate_error = RequestTypeService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el tipo de solicitud.']}
    
    @staticmethod
    def update_request_type(request_type_id: int, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Actualiza un tipo de solicitud existente.
        
        Args:
            request_type_id: ID del tipo de solicitud.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            Tupla (éxito, errores). 
            Si hay errores, el primer elemento es False y el segundo contiene los errores por campo.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = RequestTypeService.check_duplicates(data, exclude_id=request_type_id)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar tipo de solicitud {request_type_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors
        
        try:
            response = client.table('request_type').update(data).eq('id', request_type_id).execute()
            logger.info(f"✅ Tipo de solicitud ID {request_type_id} actualizado.")
            return len(response.data) > 0, {}
        except Exception as e:
            logger.error(f"❌ Error al actualizar tipo de solicitud: {e}", exc_info=True)
            # Intentar parsear error de duplicado
            duplicate_error = RequestTypeService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el tipo de solicitud.']}
    
    @staticmethod
    def delete_request_type(request_type_id: int) -> bool:
        """
        Elimina un tipo de solicitud.
        
        Args:
            request_type_id: ID del tipo de solicitud.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            response = client.table('request_type').delete().eq('id', request_type_id).execute()
            logger.info(f"🗑️ Tipo de solicitud ID {request_type_id} eliminado.")
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"❌ Error al eliminar tipo de solicitud: {e}", exc_info=True)
            return False

