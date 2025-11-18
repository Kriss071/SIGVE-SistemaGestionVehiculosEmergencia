import logging
from typing import Dict, List, Any, Optional, Tuple
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class VehicleService(WorkshopBaseService):
    """Servicio para gestionar vehículos desde la perspectiva del taller."""
    
    @staticmethod
    def search_vehicle(license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Busca un vehículo por patente.
        
        Args:
            license_plate: Patente del vehículo.
            
        Returns:
            Datos del vehículo o None si no existe.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("vehicle") \
            .select("""
                id,
                license_plate,
                brand,
                model,
                year,
                engine_number,
                vin,
                mileage,
                fire_station:fire_station_id(id, name),
                vehicle_type:vehicle_type_id(id, name),
                vehicle_status:vehicle_status_id(id, name),
                fuel_type:fuel_type_id(id, name),
                transmission_type:transmission_type_id(id, name),
                oil_type:oil_type_id(id, name),
                coolant_type:coolant_type_id(id, name)
            """) \
            .eq("license_plate", license_plate.upper())
        
        return WorkshopBaseService._execute_single(query, "search_vehicle")
    
    @staticmethod
    def search_vehicles(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca vehículos por coincidencia parcial de patente.
        
        Args:
            query: Texto a buscar dentro de la patente.
            limit: Máximo de resultados.
            
        Returns:
            Lista de vehículos que coinciden con la búsqueda.
        """
        if not query:
            return []
        
        client = WorkshopBaseService.get_client()
        query = query.upper()
        
        try:
            result = client.table("vehicle") \
                .select("""
                    id,
                    license_plate,
                    brand,
                    model,
                    year,
                    vehicle_status:vehicle_status_id(id, name)
                """) \
                .ilike("license_plate", f"%{query}%") \
                .order("license_plate") \
                .limit(limit) \
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"❌ Error buscando vehículos por patente: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _parse_duplicate_error(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado.
        
        Args:
            error: La excepción capturada.
            
        Returns:
            Diccionario con el campo duplicado y mensaje, o None si no es un error de duplicación.
        """
        from supabase import PostgrestAPIError
        
        error_msg = str(error).lower()
        error_details = getattr(error, 'message', '') or error_msg
        
        # Mapeo de campos y sus mensajes de error
        field_mapping = {
            'license_plate': {
                'keywords': ['license_plate', 'patente', 'license plate'],
                'message': 'Esta patente ya está registrada en el sistema.'
            },
            'vin': {
                'keywords': ['vin', 'chasis'],
                'message': 'Este número de chasis (VIN) ya está registrado en otro vehículo.'
            },
            'engine_number': {
                'keywords': ['engine_number', 'número de motor', 'numero de motor', 'engine number'],
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
            # Intentar extraer el nombre del constraint del mensaje
            import re
            constraint_match = re.search(r'unique constraint[^"]*"([^"]+)"', error_details, re.IGNORECASE)
            if constraint_match:
                constraint_name = constraint_match.group(1).lower()
                # Mapear nombres de constraints comunes
                if 'license_plate' in constraint_name or 'patente' in constraint_name:
                    return {'field': 'license_plate', 'message': field_mapping['license_plate']['message']}
                elif 'vin' in constraint_name or 'chasis' in constraint_name:
                    return {'field': 'vin', 'message': field_mapping['vin']['message']}
                elif 'engine_number' in constraint_name or 'motor' in constraint_name:
                    return {'field': 'engine_number', 'message': field_mapping['engine_number']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un vehículo con estos datos. Verifica que la patente, VIN y número de motor sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un vehículo.
        
        Args:
            data: Datos del vehículo a verificar.
            exclude_id: ID del vehículo a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = WorkshopBaseService.get_client()
        errors = {}
        
        # Verificar patente duplicada
        if 'license_plate' in data and data['license_plate']:
            query = client.table("vehicle") \
                .select("id", count="exact") \
                .eq("license_plate", data['license_plate'].upper())
            
            if exclude_id:
                query = query.neq("id", exclude_id)
            
            result = query.execute()
            if result.count and result.count > 0:
                errors['license_plate'] = 'Esta patente ya está registrada en el sistema.'
        
        # Verificar VIN duplicado (si se proporciona)
        if 'vin' in data and data['vin']:
            query = client.table("vehicle") \
                .select("id", count="exact") \
                .eq("vin", data['vin'])
            
            if exclude_id:
                query = query.neq("id", exclude_id)
            
            result = query.execute()
            if result.count and result.count > 0:
                errors['vin'] = 'Este número de chasis (VIN) ya está registrado en otro vehículo.'
        
        # Verificar número de motor duplicado (si se proporciona)
        if 'engine_number' in data and data['engine_number']:
            query = client.table("vehicle") \
                .select("id", count="exact") \
                .eq("engine_number", data['engine_number'])
            
            if exclude_id:
                query = query.neq("id", exclude_id)
            
            result = query.execute()
            if result.count and result.count > 0:
                errors['engine_number'] = 'Este número de motor ya está registrado en otro vehículo.'
        
        return errors
    
    @staticmethod
    def create_vehicle(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo vehículo en el sistema.
        
        Args:
            data: Datos del vehículo.
            
        Returns:
            Tupla (vehículo_creado, errores_duplicados).
            - Si se crea exitosamente: (vehículo, None)
            - Si hay errores de duplicación: (None, {campo: mensaje})
            - Si hay otro error: (None, None)
        """
        from supabase import PostgrestAPIError
        
        client = WorkshopBaseService.get_client()
        
        # Asegurar que la patente esté en mayúsculas
        if 'license_plate' in data:
            data['license_plate'] = data['license_plate'].upper()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = VehicleService.check_duplicates(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear vehículo con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            # Obtener el estado por defecto "Disponible"
            status = client.table("vehicle_status") \
                .select("id") \
                .eq("name", "Disponible") \
                .maybe_single() \
                .execute()
            
            if status.data:
                data['vehicle_status_id'] = status.data['id']
            
            result = client.table("vehicle").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Vehículo creado: {data['license_plate']}")
                return (result.data[0] if isinstance(result.data, list) else result.data), None
            return None, None
        except PostgrestAPIError as e:
            # Intentar parsear error de duplicación
            duplicate_error = VehicleService._parse_duplicate_error(e)
            if duplicate_error:
                logger.warning(f"⚠️ Error de duplicación al crear vehículo: {duplicate_error}")
                errors = {duplicate_error['field']: duplicate_error['message']}
                return None, errors
            
            logger.error(f"❌ Error de API creando vehículo: {e}", exc_info=True)
            return None, None
        except Exception as e:
            logger.error(f"❌ Error creando vehículo: {e}", exc_info=True)
            return None, None
    
    @staticmethod
    def get_all_fire_stations():
        """
        Obtiene todos los cuarteles para el selector de vehículos.
        
        Returns:
            Lista de cuarteles.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("fire_station") \
            .select("id, name, address") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_all_fire_stations")
    
    @staticmethod
    def get_catalog_data():
        """
        Obtiene todos los datos de catálogo necesarios para crear un vehículo.
        
        Returns:
            Diccionario con listas de tipos de vehículo, combustible, transmisión, etc.
        """
        client = WorkshopBaseService.get_client()
        
        catalog_data = {}
        
        try:
            # Tipos de vehículo
            catalog_data['vehicle_types'] = client.table("vehicle_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de combustible
            catalog_data['fuel_types'] = client.table("fuel_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de transmisión
            catalog_data['transmission_types'] = client.table("transmission_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de aceite
            catalog_data['oil_types'] = client.table("oil_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
            # Tipos de refrigerante
            catalog_data['coolant_types'] = client.table("coolant_type") \
                .select("id, name") \
                .order("name") \
                .execute().data or []
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de catálogo: {e}", exc_info=True)
        
        return catalog_data
    
    @staticmethod
    def get_maintenance_types():
        """
        Obtiene los tipos de mantención disponibles.
        
        Returns:
            Lista de tipos de mantención.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_type") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_maintenance_types")
    
    @staticmethod
    def get_order_statuses():
        """
        Obtiene los estados de orden disponibles.
        
        Returns:
            Lista de estados de orden.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("maintenance_order_status") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_order_statuses")
    
    @staticmethod
    def get_task_types():
        """
        Obtiene los tipos de tarea disponibles.
        
        Returns:
            Lista de tipos de tarea.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("task_type") \
            .select("id, name, description") \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_task_types")



