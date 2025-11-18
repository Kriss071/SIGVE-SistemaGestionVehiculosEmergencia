import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from supabase import PostgrestAPIError
from .base_service import FireStationBaseService

logger = logging.getLogger(__name__)


class VehicleService(FireStationBaseService):
    """
    Servicio para la gestión de vehículos del cuartel.
    """
    
    @classmethod
    def get_all_vehicles(cls, fire_station_id: int, filters: Dict = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los vehículos del cuartel con filtros opcionales.
        
        Args:
            fire_station_id: ID del cuartel.
            filters: Diccionario con filtros opcionales.
            
        Returns:
            Lista de vehículos.
        """
        logger.info(f"🚗 Obteniendo vehículos para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        query = client.table('vehicle').select(
            '*, vehicle_type(name), vehicle_status(name), fuel_type(name), '
            'transmission_type(name), oil_type(name), coolant_type(name)'
        ).eq('fire_station_id', fire_station_id)
        
        # Aplicar filtros
        if filters:
            if filters.get('status_id'):
                query = query.eq('vehicle_status_id', filters['status_id'])
            if filters.get('vehicle_type_id'):
                query = query.eq('vehicle_type_id', filters['vehicle_type_id'])
            if filters.get('license_plate'):
                query = query.ilike('license_plate', f'%{filters["license_plate"]}%')
        
        vehicles = cls._execute_query(query, 'get_all_vehicles')
        
        return vehicles
    
    @classmethod
    def get_vehicle(cls, vehicle_id: int, fire_station_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene un vehículo por su ID.
        
        Args:
            vehicle_id: ID del vehículo.
            fire_station_id: ID del cuartel (opcional, para validación).
            
        Returns:
            Datos del vehículo o None si no existe.
        """
        logger.info(f"🚗 Obteniendo vehículo {vehicle_id}")
        
        client = cls.get_client()
        
        query = client.table('vehicle').select(
            '*, vehicle_type(id, name), vehicle_status(id, name), fuel_type(id, name), '
            'transmission_type(id, name), oil_type(id, name), coolant_type(id, name), '
            'fire_station(id, name)'
        ).eq('id', vehicle_id)
        
        if fire_station_id:
            query = query.eq('fire_station_id', fire_station_id)
        
        vehicle = cls._execute_single(query, 'get_vehicle')
        
        return vehicle
    
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
            'license_plate': {
                'keywords': ['license_plate', 'patente', 'license plate'],
                'message': 'Esta patente ya está registrada en el sistema.'
            },
            'vin': {
                'keywords': ['vin', 'chasis', 'chassis'],
                'message': 'Este número de chasis (VIN) ya está registrado en otro vehículo.'
            },
            'engine_number': {
                'keywords': ['engine_number', 'motor', 'engine number', 'engine'],
                'message': 'Este número de motor ya está registrado en otro vehículo.'
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
                'message': 'Ya existe un vehículo con estos datos. Verifica que la patente, VIN y número de motor sean únicos.'
            }
        
        return None
    
    @classmethod
    def create_vehicle(cls, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo vehículo.
        
        Args:
            data: Datos del vehículo.
            
        Returns:
            Tupla (vehículo, errores). Si hay errores, el primer elemento es None.
        """
        logger.info(f"➕ Creando vehículo {data.get('license_plate')}")
        
        client = cls.get_client()
        
        # Agregar timestamps
        data['created_at'] = datetime.utcnow().isoformat()
        
        # Asegurar que los valores None se manejen correctamente (solo para campos opcionales)
        # engine_number y vin ahora son obligatorios, no se convierten a None
        for key in ['fuel_type_id', 'transmission_type_id', 
                    'oil_type_id', 'coolant_type_id', 'mileage', 'oil_capacity_liters',
                    'registration_date', 'next_revision_date']:
            if key not in data or data[key] == '':
                data[key] = None

        # Convertir Decimals a float/str para JSON (ej: oil_capacity_liters)
        for key, value in list(data.items()):
            if isinstance(value, Decimal):
                # Para cantidades numéricas preferimos float
                data[key] = float(value)
        
        try:
            # Ejecutar directamente para capturar excepciones de duplicado
            response = client.table('vehicle').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                vehicle = response.data[0]
                logger.info(f"✅ Vehículo {vehicle['id']} creado correctamente")
                return vehicle, None
            else:
                logger.error(f"❌ Error al crear vehículo: respuesta vacía")
                return None, {'general': ['Error al crear el vehículo. Por favor, intenta nuevamente.']}
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando vehículo: {e.message}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: [duplicate_error['message']]}
            
            return None, {'general': ['Error al crear el vehículo. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error inesperado creando vehículo: {e}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: [duplicate_error['message']]}
            
            return None, {'general': ['Error al crear el vehículo. Por favor, intenta nuevamente.']}
    
    @classmethod
    def update_vehicle(cls, vehicle_id: int, fire_station_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un vehículo existente.
        
        Args:
            vehicle_id: ID del vehículo.
            fire_station_id: ID del cuartel (para validación).
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores). Si hay errores, el primer elemento es False.
        """
        logger.info(f"✏️ Actualizando vehículo {vehicle_id}")
        
        client = cls.get_client()
        
        # Agregar timestamp de actualización
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Asegurar que los valores None se manejen correctamente
        for key in ['fuel_type_id', 'transmission_type_id', 'oil_type_id', 
                    'coolant_type_id', 'mileage', 'oil_capacity_liters',
                    'registration_date', 'next_revision_date', 'mileage_last_updated']:
            if key in data and data[key] == '':
                data[key] = None

        # Convertir Decimals a float/str para JSON
        for key, value in list(data.items()):
            if isinstance(value, Decimal):
                data[key] = float(value)
        
        # Los campos no editables no se incluyen en data (validado en el formulario)
        
        try:
            # Ejecutar directamente para capturar excepciones de duplicado
            response = client.table('vehicle') \
                .update(data) \
                .eq('id', vehicle_id) \
                .eq('fire_station_id', fire_station_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Vehículo {vehicle_id} actualizado correctamente")
                return True, None
            else:
                logger.error(f"❌ Error al actualizar vehículo {vehicle_id}: respuesta vacía")
                return False, {'general': ['Error al actualizar el vehículo. Por favor, intenta nuevamente.']}
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando vehículo {vehicle_id}: {e.message}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            return False, {'general': ['Error al actualizar el vehículo. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error inesperado actualizando vehículo {vehicle_id}: {e}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            return False, {'general': ['Error al actualizar el vehículo. Por favor, intenta nuevamente.']}
    
    @classmethod
    def delete_vehicle(cls, vehicle_id: int, fire_station_id: int) -> bool:
        """
        Elimina un vehículo.
        
        Args:
            vehicle_id: ID del vehículo.
            fire_station_id: ID del cuartel (para validación).
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        logger.info(f"🗑️ Eliminando vehículo {vehicle_id}")
        
        client = cls.get_client()
        
        result = cls._execute_single(
            client.table('vehicle')
                .delete()
                .eq('id', vehicle_id)
                .eq('fire_station_id', fire_station_id),
            'delete_vehicle'
        )
        
        if result:
            logger.info(f"✅ Vehículo {vehicle_id} eliminado correctamente")
            return True
        else:
            logger.error(f"❌ Error al eliminar vehículo {vehicle_id}")
            return False
    
    # Métodos para obtener catálogos
    
    @classmethod
    def get_vehicle_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de vehículos."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('vehicle_type').select('*').order('name'),
            'get_vehicle_types'
        )
    
    @classmethod
    def get_vehicle_statuses(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los estados de vehículos."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('vehicle_status').select('*').order('name'),
            'get_vehicle_statuses'
        )
    
    @classmethod
    def get_fuel_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de combustible."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('fuel_type').select('*').order('name'),
            'get_fuel_types'
        )
    
    @classmethod
    def get_transmission_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de transmisión."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('transmission_type').select('*').order('name'),
            'get_transmission_types'
        )
    
    @classmethod
    def get_oil_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de aceite."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('oil_type').select('*').order('name'),
            'get_oil_types'
        )
    
    @classmethod
    def get_coolant_types(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de refrigerante."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('coolant_type').select('*').order('name'),
            'get_coolant_types'
        )
    
    @classmethod
    def update_vehicle_status(cls, vehicle_id: int, status_id: int, user_id: str, reason: str = '') -> bool:
        """
        Actualiza el estado de un vehículo y registra el cambio en el log.
        
        Args:
            vehicle_id: ID del vehículo.
            status_id: ID del nuevo estado.
            user_id: ID del usuario que realiza el cambio.
            reason: Razón del cambio de estado.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        logger.info(f"🔄 Actualizando estado de vehículo {vehicle_id} a estado {status_id}")
        
        client = cls.get_client()
        
        # Actualizar el vehículo
        update_data = {
            'vehicle_status_id': status_id,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        vehicle_updated = cls._execute_single(
            client.table('vehicle')
                .update(update_data)
                .eq('id', vehicle_id),
            'update_vehicle_status'
        )
        
        if not vehicle_updated:
            return False
        
        # Registrar el cambio en el log
        log_data = {
            'vehicle_id': vehicle_id,
            'changed_by_user_id': user_id,
            'vehicle_status_id': status_id,
            'change_date': datetime.utcnow().isoformat(),
            'reason': reason,
            'created_at': datetime.utcnow().isoformat()
        }
        
        log_created = cls._execute_single(
            client.table('vehicle_status_log').insert(log_data),
            'create_status_log'
        )
        
        return log_created is not None
    
    @classmethod
    def get_vehicle_status_history(cls, vehicle_id: int, fire_station_id: int = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de cambios de estado de un vehículo.
        
        Args:
            vehicle_id: ID del vehículo.
            fire_station_id: ID del cuartel (opcional, para validación).
            
        Returns:
            Lista de cambios de estado.
        """
        logger.info(f"📋 Obteniendo historial de vehículo {vehicle_id}")
        
        client = cls.get_client()
        
        # Si se proporciona fire_station_id, validar que el vehículo pertenezca al cuartel
        if fire_station_id:
            vehicle = cls.get_vehicle(vehicle_id, fire_station_id)
            if not vehicle:
                logger.warning(f"Vehículo {vehicle_id} no pertenece al cuartel {fire_station_id}")
                return []
            # Log de vehículo mínimo para contexto
            try:
                logger.debug(
                    f"🔎 Vehículo validado para historial | id={vehicle.get('id')} "
                    f"patente={vehicle.get('license_plate')} estado={vehicle.get('vehicle_status', {}).get('name')}"
                )
            except Exception:
                logger.debug("🔎 Vehículo validado para historial (sin detalles por formato)")
        
        query = client.table('vehicle_status_log').select(
            '*, vehicle_status(name), changed_by:user_profile!vehicle_status_log_changed_by_user_id_fkey(first_name, last_name)'
        ).eq('vehicle_id', vehicle_id).order('change_date', desc=True)
        
        logger.debug(
            f"🧠 Ejecutando consulta de historial: tabla=vehicle_status_log, filtro vehicle_id={vehicle_id}, "
            f"order=change_date desc, include=vehicle_status(name), changed_by(first_name,last_name)"
        )
        history = cls._execute_query(query, 'get_vehicle_status_history')
        
        # Convertir fechas ISO string a objetos datetime para el template
        if history:
            for log_entry in history:
                if log_entry.get('change_date'):
                    try:
                        # Parsear fecha ISO string a datetime
                        if isinstance(log_entry['change_date'], str):
                            date_str = log_entry['change_date']
                            # Normalizar formato: reemplazar Z por +00:00 si existe
                            if date_str.endswith('Z'):
                                date_str = date_str[:-1] + '+00:00'
                            # fromisoformat maneja formato ISO con o sin microsegundos y timezone
                            log_entry['change_date'] = datetime.fromisoformat(date_str)
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"⚠️ No se pudo parsear fecha {log_entry.get('change_date')}: {e}")
                        # Mantener el valor original si falla el parseo
        
        # Logs de resultado
        try:
            total = len(history) if isinstance(history, list) else 0
            logger.info(f"📈 Historial obtenido: {total} cambio(s) para vehículo {vehicle_id}")
            if total > 0:
                sample = history[0]
                logger.info(
                    "🧾 Primer registro: "
                    f"fecha={sample.get('change_date')}, "
                    f"estado={sample.get('vehicle_status', {}).get('name')}, "
                    f"por={((sample.get('changed_by') or {}).get('first_name','') + ' ' + (sample.get('changed_by') or {}).get('last_name','')).strip()}, "
                    f"razón={sample.get('reason')}"
                )
        except Exception as e:
            logger.debug(f"ℹ️ No se pudo formatear log de historial (detalle): {e}")
        
        return history

