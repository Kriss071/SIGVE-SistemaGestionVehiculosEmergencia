import logging
import json
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class RequestService(SigveBaseService):
    """Servicio para gestionar las solicitudes de datos (data_request)."""
    
    @staticmethod
    def get_requests_by_status(status: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las solicitudes de un estado específico.
        
        Args:
            status: Estado de la solicitud (pendiente, aprobada, rechazada).
            
        Returns:
            Lista de solicitudes.
        """
        client = SigveBaseService.get_client()
        query = client.table("data_request") \
            .select("""
                *,
                request_type:request_type_id(name, description, target_table),
                requesting_user:requesting_user_id(first_name, last_name)
            """) \
            .eq("status", status) \
            .order("created_at", desc=True)
        
        return SigveBaseService._execute_query(query, f"get_requests_by_status({status})")
    
    @staticmethod
    def approve_request(request_id: int, admin_notes: str = "") -> bool:
        """
        Aprueba una solicitud y crea el registro en la tabla correspondiente.
        
        Args:
            request_id: ID de la solicitud.
            admin_notes: Notas del administrador.
            
        Returns:
            True si se aprobó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            # Obtener la solicitud
            request_data = client.table("data_request") \
                .select("*, request_type:request_type_id(target_table)") \
                .eq("id", request_id) \
                .maybe_single() \
                .execute()
            
            if not request_data.data:
                logger.warning(f"⚠️ Solicitud {request_id} no encontrada")
                return False
            
            request = request_data.data
            target_table = request['request_type']['target_table']
            requested_data = request['requested_data']
            
            # Crear el registro en la tabla correspondiente
            logger.info(f"✨ Creando registro en tabla '{target_table}' con datos: {requested_data}")
            insert_result = client.table(target_table).insert(requested_data).execute()
            
            if not insert_result.data:
                logger.error(f"❌ Error al crear registro en {target_table}")
                return False
            
            # Actualizar la solicitud como aprobada
            update_result = client.table("data_request") \
                .update({
                    "status": "aprobada",
                    "admin_notes": admin_notes
                }) \
                .eq("id", request_id) \
                .execute()
            
            logger.info(f"✅ Solicitud {request_id} aprobada correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error aprobando solicitud {request_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def reject_request(request_id: int, admin_notes: str) -> bool:
        """
        Rechaza una solicitud.
        
        Args:
            request_id: ID de la solicitud.
            admin_notes: Razón del rechazo.
            
        Returns:
            True si se rechazó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            update_result = client.table("data_request") \
                .update({
                    "status": "rechazada",
                    "admin_notes": admin_notes
                }) \
                .eq("id", request_id) \
                .execute()
            
            logger.info(f"🚫 Solicitud {request_id} rechazada")
            return True
        except Exception as e:
            logger.error(f"❌ Error rechazando solicitud {request_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_request_detail(request_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle de una solicitud específica.
        
        Args:
            request_id: ID de la solicitud.
            
        Returns:
            Datos de la solicitud o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            request_data = client.table("data_request") \
                .select("""
                    *,
                    request_type:request_type_id(name, description, target_table, form_schema),
                    requesting_user:requesting_user_id(first_name, last_name, workshop:workshop_id(name))
                """) \
                .eq("id", request_id) \
                .maybe_single() \
                .execute()
            
            return request_data.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo detalle de solicitud {request_id}: {e}", exc_info=True)
            return None


