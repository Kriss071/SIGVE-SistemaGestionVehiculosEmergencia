import logging
from typing import Any, Dict, List, Optional
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class RequestService(WorkshopBaseService):
    """
    Servicio para gestionar las solicitudes (data_request) de los talleres a SIGVE.
    """
    
    @staticmethod
    def get_all_requests(workshop_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las solicitudes de un taller con filtros opcionales.
        
        Args:
            workshop_id: ID del taller.
            filters: Filtros opcionales (status, request_type_id).
            
        Returns:
            Lista de solicitudes con información del tipo y usuario.
        """
        client = RequestService.get_client()
        
        # Primero obtener los usuarios del taller
        users_query = client.table('user_profile').select('id').eq('workshop_id', workshop_id)
        users_result = RequestService._execute_query(users_query, 'get_workshop_users')
        user_ids = [user['id'] for user in users_result]
        
        if not user_ids:
            return []
        
        # Luego obtener las solicitudes de esos usuarios
        query = (
            client.table('data_request')
            .select('*, request_type(*), user_profile!requesting_user_id(*)')
            .in_('requesting_user_id', user_ids)
            .order('created_at', desc=True)
        )
        
        # Aplicar filtros si existen
        if filters:
            if filters.get('status'):
                query = query.eq('status', filters['status'])
            if filters.get('request_type_id'):
                query = query.eq('request_type_id', filters['request_type_id'])
        
        return RequestService._execute_query(query, 'get_all_requests')
    
    @staticmethod
    def get_pending_requests_count(workshop_id: int) -> int:
        """
        Obtiene el número de solicitudes pendientes de un taller.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Número de solicitudes pendientes.
        """
        client = RequestService.get_client()
        
        # Primero obtener los usuarios del taller
        users_query = client.table('user_profile').select('id').eq('workshop_id', workshop_id)
        users_result = RequestService._execute_query(users_query, 'get_workshop_users_for_count')
        user_ids = [user['id'] for user in users_result]
        
        if not user_ids:
            return 0
        
        query = (
            client.table('data_request')
            .select('id', count='exact')
            .in_('requesting_user_id', user_ids)
            .eq('status', 'pendiente')
        )
        
        try:
            response = query.execute()
            return response.count if response.count is not None else 0
        except Exception as e:
            logger.error(f"❌ Error al contar solicitudes pendientes: {e}", exc_info=True)
            return 0
    
    @staticmethod
    def get_request(request_id: int, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una solicitud específica verificando que pertenece al taller.
        
        Args:
            request_id: ID de la solicitud.
            workshop_id: ID del taller.
            
        Returns:
            Diccionario con los datos de la solicitud o None.
        """
        client = RequestService.get_client()
        
        # Obtener la solicitud
        query = (
            client.table('data_request')
            .select('*, request_type(*), user_profile!requesting_user_id(*)')
            .eq('id', request_id)
        )
        
        request = RequestService._execute_single(query, 'get_request')
        
        # Verificar que el usuario pertenece al taller
        if request and request.get('user_profile'):
            user_workshop_id = request['user_profile'].get('workshop_id')
            if user_workshop_id == workshop_id:
                return request
        
        return None
    
    @staticmethod
    def create_request(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea una nueva solicitud.
        
        Args:
            user_id: ID del usuario que crea la solicitud.
            data: Diccionario con los campos:
                - request_type_id: ID del tipo de solicitud
                - requested_data: JSONB con los datos solicitados
                
        Returns:
            La solicitud creada o None en caso de error.
        """
        client = RequestService.get_client()
        
        request_data = {
            'requesting_user_id': user_id,
            'request_type_id': data['request_type_id'],
            'requested_data': data['requested_data'],
            'status': 'pendiente'
        }
        
        try:
            response = client.table('data_request').insert(request_data).execute()
            logger.info(f"✅ Solicitud creada correctamente por usuario {user_id}.")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ Error al crear solicitud: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_all_request_types() -> List[Dict[str, Any]]:
        """
        Obtiene todos los tipos de solicitudes disponibles.
        
        Returns:
            Lista de tipos de solicitudes.
        """
        client = RequestService.get_client()
        
        query = client.table('request_type').select('*').order('name')
        
        return RequestService._execute_query(query, 'get_all_request_types')
    
    @staticmethod
    def get_request_type(request_type_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un tipo de solicitud por su ID.
        
        Args:
            request_type_id: ID del tipo de solicitud.
            
        Returns:
            Diccionario con los datos del tipo de solicitud o None.
        """
        client = RequestService.get_client()
        
        query = client.table('request_type').select('*').eq('id', request_type_id)
        
        return RequestService._execute_single(query, 'get_request_type')

