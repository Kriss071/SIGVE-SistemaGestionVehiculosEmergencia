import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_service import FireStationBaseService

logger = logging.getLogger(__name__)


class RequestService(FireStationBaseService):
    """
    Servicio para la gestión de solicitudes de mantenimiento del cuartel.
    """
    
    @classmethod
    def get_all_requests(cls, fire_station_id: int, filters: Dict = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las solicitudes del cuartel con filtros opcionales.
        
        Args:
            fire_station_id: ID del cuartel.
            filters: Diccionario con filtros opcionales.
            
        Returns:
            Lista de solicitudes.
        """
        logger.info(f"📝 Obteniendo solicitudes para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        query = client.table('maintenance_request').select(
            '*, vehicle(id, license_plate, brand, model, year), '
            'request_type(id, name), request_status(id, name), '
            'requested_by:user_profile!maintenance_request_requested_by_user_id_fkey(first_name, last_name)'
        ).eq('fire_station_id', fire_station_id)
        
        # Aplicar filtros
        if filters:
            if filters.get('status_id'):
                query = query.eq('request_status_id', filters['status_id'])
            if filters.get('vehicle_id'):
                query = query.eq('vehicle_id', filters['vehicle_id'])
        
        query = query.order('created_at', desc=True)
        
        requests = cls._execute_query(query, 'get_all_requests')
        
        return requests
    
    @classmethod
    def get_request(cls, request_id: int, fire_station_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene una solicitud por su ID.
        
        Args:
            request_id: ID de la solicitud.
            fire_station_id: ID del cuartel (opcional, para validación).
            
        Returns:
            Datos de la solicitud o None si no existe.
        """
        logger.info(f"📝 Obteniendo solicitud {request_id}")
        
        client = cls.get_client()
        
        query = client.table('maintenance_request').select(
            '*, vehicle(id, license_plate, brand, model, year, vehicle_type(name)), '
            'request_type(id, name), request_status(id, name), '
            'requested_by:user_profile!maintenance_request_requested_by_user_id_fkey(first_name, last_name, email), '
            'workshop(id, name)'
        ).eq('id', request_id)
        
        if fire_station_id:
            query = query.eq('fire_station_id', fire_station_id)
        
        request = cls._execute_single(query, 'get_request')
        
        return request
    
    @classmethod
    def create_request(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea una nueva solicitud de mantenimiento.
        
        Args:
            data: Datos de la solicitud.
            
        Returns:
            La solicitud creada o None si falla.
        """
        logger.info(f"➕ Creando solicitud para vehículo {data.get('vehicle_id')}")
        
        client = cls.get_client()
        
        # Agregar timestamps
        data['created_at'] = datetime.utcnow().isoformat()
        
        # Estado inicial: "Pendiente" (ID 1)
        data['request_status_id'] = 1
        
        request = cls._execute_single(
            client.table('maintenance_request').insert(data),
            'create_request'
        )
        
        if request:
            logger.info(f"✅ Solicitud {request['id']} creada correctamente")
        else:
            logger.error(f"❌ Error al crear solicitud")
        
        return request
    
    @classmethod
    def cancel_request(cls, request_id: int, fire_station_id: int) -> bool:
        """
        Cancela una solicitud de mantenimiento.
        
        Args:
            request_id: ID de la solicitud.
            fire_station_id: ID del cuartel (para validación).
            
        Returns:
            True si se canceló correctamente, False en caso contrario.
        """
        logger.info(f"❌ Cancelando solicitud {request_id}")
        
        client = cls.get_client()
        
        # Estado cancelado: "Cancelada" (ID 5)
        data = {
            'request_status_id': 5,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = cls._execute_single(
            client.table('maintenance_request')
                .update(data)
                .eq('id', request_id)
                .eq('fire_station_id', fire_station_id)
                .in_('request_status_id', [1, 2]),  # Solo si está pendiente o en revisión
            'cancel_request'
        )
        
        if result:
            logger.info(f"✅ Solicitud {request_id} cancelada correctamente")
            return True
        else:
            logger.error(f"❌ Error al cancelar solicitud {request_id}")
            return False
    
    @classmethod
    def get_request_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de solicitudes."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('request_type').select('*').order('name'),
            'get_request_types'
        )
    
    @classmethod
    def get_request_statuses(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los estados de solicitudes."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('request_status').select('*').order('id'),
            'get_request_statuses'
        )

