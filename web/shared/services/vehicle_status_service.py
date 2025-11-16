"""
Servicio compartido para la gestión de estados de vehículos.

Este servicio centraliza la lógica de actualización de estados de vehículos
y el registro de cambios en el historial (vehicle_status_log).
Puede ser utilizado tanto por fire_station como por workshop.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from accounts.client.supabase_client import get_supabase

logger = logging.getLogger(__name__)


class VehicleStatusService:
    """Servicio para gestionar cambios de estado de vehículos."""
    
    @staticmethod
    def get_status_by_name(status_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un estado de vehículo por su nombre.
        
        Args:
            status_name: Nombre del estado (ej: "En Mantención", "Disponible").
            
        Returns:
            Dict con información del estado o None si no existe.
        """
        try:
            client = get_supabase()
            result = client.table('vehicle_status') \
                .select('id, name') \
                .ilike('name', status_name) \
                .maybe_single() \
                .execute()
            
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado '{status_name}': {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_vehicle_status(
        vehicle_id: int,
        status_id: int,
        user_id: str,
        reason: str = '',
        auto_generated: bool = False
    ) -> bool:
        """
        Actualiza el estado de un vehículo y registra el cambio en el historial.
        
        Args:
            vehicle_id: ID del vehículo.
            status_id: ID del nuevo estado.
            user_id: ID del usuario que realiza el cambio.
            reason: Razón del cambio de estado.
            auto_generated: Si True, indica que el cambio fue automático (por el sistema).
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        try:
            client = get_supabase()
            
            # Obtener el estado actual del vehículo antes de actualizar
            current_vehicle = client.table('vehicle') \
                .select('vehicle_status_id') \
                .eq('id', vehicle_id) \
                .maybe_single() \
                .execute()
            
            if not current_vehicle.data:
                logger.error(f"❌ Vehículo {vehicle_id} no encontrado")
                return False
            
            current_status_id = current_vehicle.data.get('vehicle_status_id')
            
            # Si el estado es el mismo, no hacer nada
            if current_status_id == status_id:
                logger.debug(f"ℹ️ Vehículo {vehicle_id} ya tiene el estado {status_id}")
                return True
            
            # Actualizar el estado del vehículo
            update_data = {
                'vehicle_status_id': status_id,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            vehicle_updated = client.table('vehicle') \
                .update(update_data) \
                .eq('id', vehicle_id) \
                .execute()
            
            if not vehicle_updated.data:
                logger.error(f"❌ Error actualizando estado del vehículo {vehicle_id}")
                return False
            
            # Preparar el mensaje de razón
            if auto_generated and not reason:
                reason = 'Cambio automático generado por el sistema'
            elif auto_generated and reason:
                reason = f'Automático: {reason}'
            
            # Registrar el cambio en el log
            log_data = {
                'vehicle_id': vehicle_id,
                'changed_by_user_id': user_id,
                'vehicle_status_id': status_id,
                'change_date': datetime.utcnow().isoformat(),
                'reason': reason or ''
            }
            
            try:
                log_created = client.table('vehicle_status_log') \
                    .insert(log_data) \
                    .execute()
                
                if log_created.data:
                    logger.info(f"✅ Estado del vehículo {vehicle_id} actualizado a {status_id} y registrado en historial")
                    return True
                else:
                    logger.warning(f"⚠️ Estado del vehículo {vehicle_id} actualizado pero no se registró en historial")
                    logger.warning(f"⚠️ Log data que intentó insertar: {log_data}")
                    return True  # El cambio de estado se hizo, aunque falló el log
            except Exception as log_error:
                logger.error(f"❌ Error al insertar en vehicle_status_log: {log_error}", exc_info=True)
                logger.error(f"❌ Datos que intentó insertar: {log_data}")
                return True  # El cambio de estado se hizo, aunque falló el log
            
        except Exception as e:
            logger.error(f"❌ Error actualizando estado del vehículo {vehicle_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def update_vehicle_status_by_name(
        vehicle_id: int,
        status_name: str,
        user_id: str,
        reason: str = '',
        auto_generated: bool = False
    ) -> bool:
        """
        Actualiza el estado de un vehículo usando el nombre del estado.
        
        Args:
            vehicle_id: ID del vehículo.
            status_name: Nombre del estado (ej: "En Mantención").
            user_id: ID del usuario que realiza el cambio.
            reason: Razón del cambio de estado.
            auto_generated: Si True, indica que el cambio fue automático.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        status = VehicleStatusService.get_status_by_name(status_name)
        
        if not status:
            logger.error(f"❌ Estado '{status_name}' no encontrado en la base de datos")
            return False
        
        return VehicleStatusService.update_vehicle_status(
            vehicle_id=vehicle_id,
            status_id=status['id'],
            user_id=user_id,
            reason=reason,
            auto_generated=auto_generated
        )

