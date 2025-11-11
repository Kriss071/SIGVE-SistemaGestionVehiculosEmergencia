import logging
from typing import Any, Dict, List, Optional
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
    def create_request_type(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo tipo de solicitud.
        
        Args:
            data: Diccionario con los campos:
                - name: Nombre del tipo de solicitud
                - description: Descripción (opcional)
                - target_table: Tabla objetivo donde se guardará la data
                - form_schema: JSONB con el esquema del formulario
                
        Returns:
            El tipo de solicitud creado o None en caso de error.
        """
        client = SigveBaseService.get_client()
        
        try:
            response = client.table('request_type').insert(data).execute()
            logger.info(f"✅ Tipo de solicitud '{data['name']}' creado correctamente.")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Error al crear tipo de solicitud: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_request_type(request_type_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un tipo de solicitud existente.
        
        Args:
            request_type_id: ID del tipo de solicitud.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            response = client.table('request_type').update(data).eq('id', request_type_id).execute()
            logger.info(f"✅ Tipo de solicitud ID {request_type_id} actualizado.")
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"❌ Error al actualizar tipo de solicitud: {e}", exc_info=True)
            return False
    
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

