import logging
import json
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService
from supabase import PostgrestAPIError

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
                request_type:request_type_id(name, description, target_table, form_schema),
                requesting_user:requesting_user_id(first_name, last_name)
            """) \
            .eq("status", status) \
            .order("created_at", desc=True)
        
        return SigveBaseService._execute_query(query, f"get_requests_by_status({status})")
    
    @staticmethod
    def approve_request(request_id: int, admin_notes: str = "", auto_create: bool = True, edited_data: Optional[Dict[str, Any]] = None) -> dict:
        """
        Aprueba una solicitud y opcionalmente crea el registro en la tabla correspondiente.
        
        Args:
            request_id: ID de la solicitud.
            admin_notes: Notas del administrador.
            auto_create: Si es True, crea el registro automáticamente. Si es False, solo marca como aprobada.
            edited_data: Datos editados por el administrador. Si se proporciona, se usarán en lugar de requested_data.
            
        Returns:
            Dict con 'success' (bool) y 'error' (str opcional) con el mensaje de error específico.
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
                error_msg = f"Solicitud {request_id} no encontrada"
                logger.warning(f"⚠️ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            request = request_data.data
            
            # Validar que existe request_type
            if not request.get('request_type'):
                error_msg = f"Solicitud {request_id} no tiene tipo de solicitud asociado"
                logger.error(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            target_table = request['request_type'].get('target_table')
            if not target_table:
                error_msg = f"Solicitud {request_id} no tiene tabla objetivo definida"
                logger.error(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            # Usar datos editados si se proporcionaron, sino usar los originales
            requested_data = edited_data if edited_data else request.get('requested_data')
            if not requested_data:
                error_msg = f"Solicitud {request_id} no tiene datos solicitados"
                logger.error(f"❌ {error_msg}")
                return {'success': False, 'error': error_msg}
            
            # Crear el registro en la tabla correspondiente solo si auto_create está activado
            if auto_create:
                try:
                    logger.info(f"✨ Creando registro en tabla '{target_table}' con datos: {requested_data}")
                    insert_result = client.table(target_table).insert(requested_data).execute()
                    
                    if not insert_result.data:
                        # Intentar obtener más detalles del error de la respuesta
                        error_details = "No se pudo crear el registro. Verifica los logs del servidor para más detalles."
                        
                        # Revisar si hay información de error en la respuesta
                        if hasattr(insert_result, 'data') and insert_result.data is not None:
                            if isinstance(insert_result.data, dict) and 'message' in insert_result.data:
                                error_details = insert_result.data['message']
                            elif isinstance(insert_result.data, list) and len(insert_result.data) == 0:
                                error_details = "La tabla no devolvió ningún registro después de la inserción."
                        
                        error_msg = f"Error al crear el registro en la tabla '{target_table}'. {error_details}"
                        logger.error(f"❌ {error_msg}. Respuesta: {insert_result}")
                        return {'success': False, 'error': error_msg}
                except PostgrestAPIError as e:
                    # Error específico de Supabase/PostgreSQL
                    error_msg = f"Error de base de datos al crear registro en '{target_table}'"
                    
                    # Intentar extraer mensaje de error más específico
                    if hasattr(e, 'message') and e.message:
                        error_msg = f"Error al crear registro en '{target_table}': {e.message}"
                    elif hasattr(e, 'details') and e.details:
                        error_msg = f"Error al crear registro en '{target_table}': {e.details}"
                    elif hasattr(e, 'hint') and e.hint:
                        error_msg = f"Error al crear registro en '{target_table}': {e.hint}"
                    elif hasattr(e, 'code'):
                        error_msg = f"Error de base de datos ({e.code}) al crear registro en '{target_table}': {str(e)}"
                    else:
                        # Si no hay detalles específicos, usar el string del error
                        error_str = str(e)
                        if error_str and error_str != 'None':
                            error_msg = f"Error al crear registro en '{target_table}': {error_str}"
                    
                    logger.error(f"❌ {error_msg}", exc_info=True)
                    return {'success': False, 'error': error_msg}
                except Exception as e:
                    error_msg = f"Error inesperado al crear registro en tabla '{target_table}': {str(e)}"
                    logger.error(f"❌ {error_msg}", exc_info=True)
                    return {'success': False, 'error': error_msg}
            
            # Actualizar la solicitud como aprobada
            try:
                update_result = client.table("data_request") \
                    .update({
                        "status": "aprobada",
                        "admin_notes": admin_notes
                    }) \
                    .eq("id", request_id) \
                    .execute()
                
                if not update_result.data:
                    error_msg = f"Error al actualizar solicitud {request_id} como aprobada"
                    logger.error(f"❌ {error_msg}")
                    return {'success': False, 'error': error_msg}
            except Exception as e:
                error_msg = f"Error al actualizar solicitud como aprobada: {str(e)}"
                logger.error(f"❌ {error_msg}", exc_info=True)
                return {'success': False, 'error': error_msg}
            
            if auto_create:
                logger.info(f"✅ Solicitud {request_id} aprobada correctamente y registro creado en {target_table}")
            else:
                logger.info(f"✅ Solicitud {request_id} aprobada correctamente (creación automática deshabilitada)")
            
            return {'success': True}
        except Exception as e:
            error_msg = f"Error inesperado al aprobar solicitud: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return {'success': False, 'error': error_msg}
    
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


