import logging
from typing import Dict, List, Any, Optional, Tuple
from .base_service import SigveBaseService
from supabase import PostgrestAPIError

logger = logging.getLogger(__name__)


class FireStationService(SigveBaseService):
    """Servicio para gestionar cuarteles de bomberos."""
    
    @staticmethod
    def get_all_fire_stations() -> List[Dict[str, Any]]:
        """
        Obtiene todos los cuarteles con información adicional.
        
        Returns:
            Lista de cuarteles.
        """
        client = SigveBaseService.get_client()
        query = client.table("fire_station") \
            .select("""
                *,
                commune:commune_id(name, province:province_id(name, region:region_id(name)))
            """) \
            .order("name")
        
        fire_stations = SigveBaseService._execute_query(query, "get_all_fire_stations")
        
        # Contar vehículos para cada cuartel
        for station in fire_stations:
            try:
                vehicles_count = client.table("vehicle") \
                    .select("id", count="exact") \
                    .eq("fire_station_id", station['id']) \
                    .execute()
                station['vehicles_count'] = vehicles_count.count or 0
            except Exception as e:
                logger.error(f"❌ Error contando vehículos del cuartel {station['id']}: {e}")
                station['vehicles_count'] = 0
        
        return fire_stations
    
    @staticmethod
    def get_fire_station(fire_station_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cuartel específico por ID.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            Datos del cuartel o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station") \
                .select("""
                    *,
                    commune:commune_id(name, province:province_id(name, region:region_id(name)))
                """) \
                .eq("id", fire_station_id) \
                .maybe_single() \
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo cuartel {fire_station_id}: {e}", exc_info=True)
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
            'name': {
                'keywords': ['name', 'nombre'],
                'message': 'Este nombre de cuartel ya está registrado.'
            },
            'address': {
                'keywords': ['address', 'dirección', 'direccion'],
                'message': 'Esta dirección ya está registrada en otro cuartel.'
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
                if 'name' in constraint_name:
                    return {'field': 'name', 'message': field_mapping['name']['message']}
                elif 'address' in constraint_name:
                    return {'field': 'address', 'message': field_mapping['address']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un cuartel con estos datos. Verifica que el nombre y dirección sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates(data: Dict[str, Any], exclude_id: Optional[int] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un cuartel.
        
        Args:
            data: Datos del cuartel a verificar.
            exclude_id: ID del cuartel a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        client = SigveBaseService.get_client()
        errors = {}
        
        # Verificar nombre duplicado
        if data.get('name'):
            query = client.table("fire_station").select("id, name").eq("name", data['name'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['name'] = 'Este nombre de cuartel ya está registrado.'
        
        # Verificar dirección duplicada
        if data.get('address'):
            query = client.table("fire_station").select("id, name").eq("address", data['address'])
            if exclude_id:
                query = query.neq("id", exclude_id)
            existing = query.execute()
            if existing.data and len(existing.data) > 0:
                errors['address'] = 'Esta dirección ya está registrada en otro cuartel.'
        
        return errors
    
    @staticmethod
    def create_fire_station(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Crea un nuevo cuartel.
        
        Args:
            data: Datos del cuartel (name, address, commune_id).
            
        Returns:
            Tupla (cuartel_creado, errores):
            - cuartel_creado: Datos del cuartel creado o None si hubo error.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar crear
        duplicate_errors = FireStationService.check_duplicates(data)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear cuartel con datos duplicados: {duplicate_errors}")
            return None, duplicate_errors
        
        try:
            result = client.table("fire_station").insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Cuartel creado: {data.get('name')}")
                return (result.data[0] if isinstance(result.data, list) else result.data, None)
            return None, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando cuartel: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = FireStationService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el cuartel. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error creando cuartel: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = FireStationService._parse_duplicate_error(e)
            if duplicate_error:
                return None, {duplicate_error['field']: duplicate_error['message']}
            return None, {'general': ['Error al crear el cuartel. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def update_fire_station(fire_station_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un cuartel existente.
        
        Args:
            fire_station_id: ID del cuartel.
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        
        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = FireStationService.check_duplicates(data, exclude_id=fire_station_id)
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar cuartel {fire_station_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors
        
        try:
            result = client.table("fire_station") \
                .update(data) \
                .eq("id", fire_station_id) \
                .execute()
            
            logger.info(f"✅ Cuartel {fire_station_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando cuartel {fire_station_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = FireStationService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el cuartel. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error actualizando cuartel {fire_station_id}: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = FireStationService._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el cuartel. Por favor, intenta nuevamente.']}
    
    @staticmethod
    def delete_fire_station(fire_station_id: int) -> bool:
        """
        Elimina un cuartel.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("fire_station") \
                .delete() \
                .eq("id", fire_station_id) \
                .execute()
            
            logger.info(f"🗑️ Cuartel {fire_station_id} eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando cuartel {fire_station_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_all_communes() -> List[Dict[str, Any]]:
        """
        Obtiene todas las comunas para formularios.
        
        Returns:
            Lista de comunas con provincia y región.
        """
        client = SigveBaseService.get_client()
        query = client.table("commune") \
            .select("""
                *,
                province:province_id(name, region:region_id(name))
            """) \
            .order("name")
        
        return SigveBaseService._execute_query(query, "get_all_communes")


