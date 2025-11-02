from datetime import date, datetime
from decimal import Decimal
import logging
from typing import Any
from .base import VehicleService
from accounts.client.supabase_client import get_supabase_with_user
from shared.services.base_service import BaseService

logger = logging.getLogger(__name__)


class SupabaseVehicleService(BaseService, VehicleService):
    """
    Implementación concreta de VehicleService que interactúa con Supabase.
    Hereda de BaseService para la inicialización del cliente.
    
    Esta clase maneja toda la lógica de obtención, creación y búsqueda de vehículos
    utilizando la API de Supabase a través de la biblioteca `supabase-py`.
    Hereda de la clase base abstracta VehicleService, garantizando que implementa
    todos los métodos requeridos por la interfaz.
    """

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.

        Args:
            token: El token de acceso JWT del usuario actual.
            refresh_token: El token de refresco del usuario actual.
        """
        # Crea y almacena una instancia del cliente Supabase autenticado para este servicio
        super().__init__(token, refresh_token)
        logger.debug("🔧 Instancia de SupabaseVehicleService creada.")


    def list_vehicles(self) -> list[dict[str, Any]]:
        """
        Obtiene una lista de todos los vehículos registrados, incluyendo datos de relaciones.

        Consulta la tabla 'vehicle' y trae información relacionada de otras tablas
        (como fire_station, vehicle_type, etc.) usando la sintaxis de "join" de Supabase
        dentro del método `select()`. Normaliza la estructura de datos anidada
        devuelta por Supabase a una estructura plana para facilitar su uso.

        Returns:
            Una lista de diccionarios, donde cada diccionario representa un vehículo
            con sus datos relacionados aplanados (ej. 'fire_station_name').
            Retorna una lista vacía si ocurre un error.
        """

        try:
            logger.info("🚒 Gettings vehicles...")
            # Construir y ejecutar la consulta a Supabase
            # El string multilinea en select() especifica:
            #   '*': Todas las columnas de la tabla 'vehicle'.
            #   'nombre_alias:columna_fk(columnas_relacionadas)': Trae datos de tablas relacionadas.
            response = (
                self.client.table("vehicle")
                .select(
                    """
                    *, 
                    fire_station:fire_station_id(name, address),
                    vehicle_type:vehicle_type_id(name),
                    vehicle_status:vehicle_status_id(name),
                    fuel_type:fuel_type_id(name),
                    transmission_type:transmission_type_id(name),
                    oil_type:oil_type_id(name),
                    coolant_type:coolant_type_id(name)
                    """
                )
                .execute()
            )
            logger.debug(f"📊 Respuesta cruda de Supabase (list_vehicles): {response.data}")

            # Normalización de Datos:
            # Supabase devuelve los datos relacionados como diccionarios anidados.
            # Este bucle recorre cada vehículo 'v' en la respuesta y crea un nuevo
            # diccionario 'normalized' con una estructura plana, extrayendo los nombres
            # de las entidades relacionadas. Esto simplifica el acceso en las plantillas Django.
            vehicles = []
            for v in response.data:
                normalized = {
                    # Copiar campos directos de 'vehicle', usando .get() con valores por defecto
                    'id': v['id'],
                    'license_plate': v.get('license_plate', ''),
                    'brand': v.get('brand', ''),
                    'model': v.get('model', ''),
                    'year': v.get('year', 0),
                    'engine_number': v.get('engine_number'),
                    'vin': v.get('vin'),
                    'mileage': v.get('mileage'),
                    'mileage_last_updated': v.get('mileage_last_updated'),
                    'oil_capacity_liters': v.get('oil_capacity_liters'),
                    'registration_date': v.get('registration_date'),
                    'next_revision_date': v.get('next_revision_date'),
                    
                    # Extraer nombres de las relaciones:
                    # v.get('fire_station', {}): Obtiene el dict anidado o uno vacío si no existe.
                    # .get('name'): Obtiene el nombre dentro del dict anidado.
                    # isinstance(v.get('fire_station'), dict): Asegura que solo intentamos .get('name') si es un diccionario.
                    'fire_station_name': v.get('fire_station', {}).get('name') if isinstance(v.get('fire_station'), dict) else None,
                    'vehicle_type_name': v.get('vehicle_type', {}).get('name') if isinstance(v.get('vehicle_type'), dict) else None,
                    'vehicle_status_name': v.get('vehicle_status', {}).get('name') if isinstance(v.get('vehicle_status'), dict) else None,
                    'fuel_type_name': v.get('fuel_type', {}).get('name') if isinstance(v.get('fuel_type'), dict) else None,
                    'transmission_type_name': v.get('transmission_type', {}).get('name') if isinstance(v.get('transmission_type'), dict) else None,
                    'oil_type_name': v.get('oil_type', {}).get('name') if isinstance(v.get('oil_type'), dict) else None,
                    'coolant_type_name': v.get('coolant_type', {}).get('name') if isinstance(v.get('coolant_type'), dict) else None,
                }
                vehicles.append(normalized)
            
            logger.info(f"✅ Se listaron {len(vehicles)} vehículos correctamente.")
            return vehicles # Devuelve la lista de vehículos normalizados

        except Exception as e:
            # Captura cualquier excepción durante la llamada a Supabase o la normalización
            logger.error(f"❌ Error al listar vehículos: {e}", exc_info=True) # exc_info=True incluye el traceback
            return [] # Devuelve lista vacía en caso de error    
    
    def add_vehicle(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Agrega un nuevo vehículo a la base de datos Supabase.

        Realiza pre-procesamiento de los datos:
        - Convierte objetos `date` y `datetime` a strings en formato ISO 8601.
        - Convierte strings vacíos o compuestos solo de espacios en blanco a `None`
          para campos que pueden ser nulos en la base de datos.

        Args:
            data: Un diccionario con los datos del vehículo a insertar. 
                  Se espera que las claves coincidan con los nombres de las columnas
                  en la tabla 'vehicle' de Supabase.

        Returns:
            Una lista conteniendo el diccionario del vehículo recién creado si la
            inserción fue exitosa, según la respuesta de Supabase.
            Puede devolver una lista vacía si la inserción falla.
        """

        try:
            logger.info(f"➕ Intentando agregar vehículo con datos: {data}")
            # Crear un nuevo diccionario para los datos procesados
            processed_data = {} 

            for key, value in data.items():
                if key == 'id':
                    logger.debug("🗑️ Campo 'id' encontrado en los datos, será excluido de la inserción.")
                    continue # Saltar a la siguiente iteración, no incluir 'id'
                
                # Convertir fechas/datetimes a string ISO para Supabase
                if isinstance(value, (date, datetime)):
                    processed_data[key] = value.isoformat()
                    logger.debug(f"🔄 Campo '{key}' convertido a ISO format: {processed_data[key]}")
                # Convertir Decimal a float para serialización JSON
                elif isinstance(value, Decimal):
                    processed_data[key] = float(value)
                    logger.debug(f"🔄 Campo '{key}' (Decimal) convertido a float: {processed_data[key]}")
                # Convertir strings vacíos o solo espacios a None si el campo puede ser nulo
                elif isinstance(value, str) and not value.strip():
                     # Campos opcionales aceptan None en la BD
                    processed_data[key] = None
                    logger.debug(f"🔄 Campo string vacío '{key}' convertido a None.")
                else:
                    # Mantener el valor original si no es fecha ni string vacío
                    processed_data[key] = value

            # Intentar insertar los datos procesados en la tabla 'vehicle'
            response = self.client.table("vehicle").insert(processed_data).execute()
            logger.debug(f"📊 Respuesta cruda de Supabase (add_vehicle): {response.data}")

            # Verificar si la operación fue exitosa
            if response.data:
                 logger.info(f"✅ Vehículo agregado exitosamente: {response.data[0].get('license_plate', 'ID: '+str(response.data[0].get('id')))}")
                 return response.data # Devuelve la data insertada
            else:
                 # Si Supabase no devuelve datos, podría indicar un error no capturado como excepción
                 logger.warning("⚠️ Supabase no devolvió datos después de la inserción.")
                 return [] # O considera lanzar una excepción personalizada aquí

        except Exception as e:
            # Capturar errores durante la inserción (ej. violación de constraints, error de red)
            logger.error(f"❌ Error al agregar vehículo: {e}", exc_info=True)
            return [] # Devolver lista vacía en caso de error

    def search_vehicles(self, query: str) -> list[dict[str, Any]]:
        """
        Busca vehículos en Supabase cuyos campos coincidan (parcialmente, sin importar
        mayúsculas/minúsculas) con el término de búsqueda proporcionado.

        Busca en 'license_plate', 'brand' y 'model'. Si la consulta es un número,
        también filtra adicionalmente por vehículos cuyo año ('year') comience con
        dicho número. Normaliza los resultados a una estructura plana.

        Args:
            query: El término de búsqueda (string).

        Returns:
            Una lista de diccionarios con los vehículos que coinciden, con una
            estructura de datos aplanada. Lista vacía si no hay coincidencias o si
            ocurre un error.
        """

        # Si la consulta está vacía, simplemente devuelve todos los vehículos
        if not query:
            logger.debug("📂 Búsqueda vacía, listando todos los vehículos.")
            return self.list_vehicles()

        try:
            # Convertir la consulta a minúsculas para búsqueda case-insensitive
            q = query.lower()
            logger.info(f"🔍 Buscando vehículos con consulta: '{q}'")

            # Construir la consulta a Supabase usando or_() para buscar en múltiples campos
            # 'ilike' realiza una búsqueda case-insensitive con patrones SQL (.*{q}* busca q en cualquier parte)
            response = (
                self.client.table("vehicle")
                .select( # Seleccionar columnas necesarias y relaciones para normalización
                    """
                    *, 
                    fire_station:fire_station_id(name),
                    vehicle_type:vehicle_type_id(name),
                    vehicle_status:vehicle_status_id(name),
                    fuel_type:fuel_type_id(name),
                    transmission_type:transmission_type_id(name)
                    """
                )
                .or_( # Buscar si 'q' aparece en cualquiera de estos campos
                    f"license_plate.ilike.*{q}*," 
                    f"brand.ilike.*{q}*," 
                    f"model.ilike.*{q}*"
                    # AÑADIR MÁS ADELANTE
                    # Podrías añadir más campos aquí si es necesario, ej: f"vin.ilike.*{q}*"
                )
                .execute()
            )
            logger.debug(f"📊 Respuesta cruda de Supabase (search_vehicles): {response.data}")

            results = [] # Lista para almacenar los resultados finales (normalizados y filtrados)

            # --- Filtrado adicional por Año si la consulta es numérica ---
            if q.isdigit():
                logger.debug(f"🔢 Consulta numérica detectada ('{q}'). Filtrando por año...")
                initial_results_count = len(response.data)
                # Iterar sobre los resultados iniciales de Supabase
                for v in response.data:
                    # Obtener el año como string, si existe, y verificar si comienza con 'q'
                    if str(v.get("year", "")).startswith(q):
                        # Si coincide, normalizar este vehículo y añadirlo a 'results'
                        normalized = {
                             # Copiar campos básicos
                            'id': v['id'],
                            'license_plate': v.get('license_plate', ''),
                            'brand': v.get('brand', ''),
                            'model': v.get('model', ''),
                            'year': v.get('year', 0),
                            'mileage': v.get('mileage'), # Añadido kilometraje
                             # Normalizar relaciones (similar a list_vehicles, adaptado a lo que devuelve el select)
                            'vehicle_type_name': v.get('vehicle_type', {}).get('name') if isinstance(v.get('vehicle_type'), dict) else None,
                            'vehicle_status_name': v.get('vehicle_status', {}).get('name') if isinstance(v.get('vehicle_status'), dict) else None,
                            # Nota: fire_station, fuel_type, etc., no se piden en el select de búsqueda,
                            # por lo que no estarán disponibles aquí a menos que se añadan al select.
                        }
                        results.append(normalized)
                logger.debug(f"🔢 Filtrado por año completado. {len(results)} de {initial_results_count} coincidieron.")
                
            # --- Normalización si la consulta NO es numérica ---
            else:
                 logger.debug(" Consulta no numérica. Normalizando todos los resultados de Supabase.")
                 # Iterar sobre todos los resultados de Supabase y normalizarlos
                 for v in response.data:
                     normalized = {
                         # Copiar campos básicos
                         'id': v['id'],
                         'license_plate': v.get('license_plate', ''),
                         'brand': v.get('brand', ''),
                         'model': v.get('model', ''),
                         'year': v.get('year', 0),
                         'mileage': v.get('mileage'), # Añadido kilometraje
                          # Normalizar relaciones (igual que en el bloque 'if q.isdigit()')
                         'vehicle_type_name': v.get('vehicle_type', {}).get('name') if isinstance(v.get('vehicle_type'), dict) else None,
                         'vehicle_status_name': v.get('vehicle_status', {}).get('name') if isinstance(v.get('vehicle_status'), dict) else None,
                     }
                     results.append(normalized)

            logger.info(f"✅ Búsqueda completada. Se encontraron {len(results)} vehículos.")
            return results # Devolver la lista final de resultados normalizados (y filtrados por año si aplicaba)

        except Exception as e:
            # Capturar errores durante la búsqueda
            logger.error(f"❌ Error al buscar vehículos con consulta '{query}': {e}", exc_info=True)
            return [] # Devolver lista vacía en caso de error

    def get_vehicle(self, license_plate: str) -> dict[str, Any] | None:
        """
        Obtiene los detalles completos de un vehículo específico por su patente.

        Busca en la tabla 'vehicle' usando la `license_plate` proporcionada.
        Utiliza `maybe_single()` para esperar como máximo un resultado.
        Incluye y normaliza datos de todas las relaciones (similar a `list_vehicles`).

        Args:
            license_plate: La patente (string) exacta del vehículo a buscar.

        Returns:
            Un diccionario con los datos completos y normalizados del vehículo si se
            encuentra.
            None si no se encuentra ningún vehículo con esa patente o si ocurre un error.
        """
        try:
            logger.info(f"ℹ️ Obteniendo detalles para vehículo con patente: '{license_plate}'")
            # Construir y ejecutar la consulta a Supabase
            response = (
                self.client.table("vehicle")
                .select( # Pedir todas las columnas y todas las relaciones
                    """
                    *, 
                    fire_station:fire_station_id(name, address),
                    vehicle_type:vehicle_type_id(name),
                    vehicle_status:vehicle_status_id(name),
                    fuel_type:fuel_type_id(name),
                    transmission_type:transmission_type_id(name),
                    oil_type:oil_type_id(name),
                    coolant_type:coolant_type_id(name)
                    """
                )
                 # Filtrar exactamente por la patente proporcionada
                .eq("license_plate", license_plate)
                 # Indicar a Supabase que esperamos 0 o 1 resultado, no una lista
                .maybe_single() 
                .execute()
            )
            logger.debug(f"📊 Respuesta cruda de Supabase (get_vehicle): {response.data}")

            # Si se encontró un vehículo (response.data no es None)
            if response.data:
                v = response.data # El resultado ya es un diccionario gracias a maybe_single()
                # Normalizar los datos (similar a list_vehicles)
                normalized_vehicle = {
                    'id': v['id'],
                    'license_plate': v.get('license_plate', ''),
                    'brand': v.get('brand', ''),
                    'model': v.get('model', ''),
                    'year': v.get('year', 0),
                    'engine_number': v.get('engine_number'),
                    'vin': v.get('vin'),
                    'mileage': v.get('mileage'),
                    'mileage_last_updated': v.get('mileage_last_updated'),
                    'oil_capacity_liters': v.get('oil_capacity_liters'),
                    'registration_date': v.get('registration_date'),
                    'next_revision_date': v.get('next_revision_date'),
                    # Extraer nombres de relaciones
                    'fire_station_name': v.get('fire_station', {}).get('name') if isinstance(v.get('fire_station'), dict) else None,
                    'vehicle_type_name': v.get('vehicle_type', {}).get('name') if isinstance(v.get('vehicle_type'), dict) else None,
                    'vehicle_status_name': v.get('vehicle_status', {}).get('name') if isinstance(v.get('vehicle_status'), dict) else None,
                    'fuel_type_name': v.get('fuel_type', {}).get('name') if isinstance(v.get('fuel_type'), dict) else None,
                    'transmission_type_name': v.get('transmission_type', {}).get('name') if isinstance(v.get('transmission_type'), dict) else None,
                    'oil_type_name': v.get('oil_type', {}).get('name') if isinstance(v.get('oil_type'), dict) else None,
                    'coolant_type_name': v.get('coolant_type', {}).get('name') if isinstance(v.get('coolant_type'), dict) else None,
                    # Puedes añadir aquí otros campos si son necesarios para la vista de detalle
                }
                logger.info(f"✅ Vehículo encontrado y normalizado: {license_plate}")
                return normalized_vehicle # Devolver el diccionario normalizado
            else:
                # Si response.data es None, el vehículo no existe
                logger.warning(f"⚠️ No se encontró vehículo con patente: {license_plate}")
                return None # Devolver None para indicar que no se encontró

        except Exception as e:
            # Capturar errores durante la obtención del vehículo
            logger.error(f"❌ Error al obtener vehículo '{license_plate}': {e}", exc_info=True)
            return None # Devolver None en caso de error

    def delete_vehicle(self, license_plate: str) -> bool:
        """
        Elimina un vehículo de la base de datos Supabase por su patente.

        Realiza una eliminación directa en la tabla 'vehicle' usando la patente
        como identificador. Verifica que el vehículo exista antes de intentar eliminarlo.

        Args:
            license_plate: La patente (string) del vehículo a eliminar.

        Returns:
            True si la eliminación fue exitosa, False si el vehículo no existe
            o si ocurre un error durante la eliminación.
        """
        try:
            logger.info(f"🗑️ Intentando eliminar vehículo con patente: '{license_plate}'")
            
            # Verificar que el vehículo existe antes de eliminarlo
            vehicle = self.get_vehicle(license_plate)
            if not vehicle:
                logger.warning(f"⚠️ No se puede eliminar: vehículo con patente '{license_plate}' no encontrado.")
                return False

            # Realizar la eliminación en Supabase
            response = (
                self.client.table("vehicle")
                .delete()
                .eq("license_plate", license_plate)
                .execute()
            )

            # Verificar que la eliminación fue exitosa
            # Supabase devuelve los datos eliminados en response.data
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Vehículo eliminado exitosamente: {license_plate}")
                return True
            else:
                logger.warning(f"⚠️ La eliminación no devolvió datos para la patente: '{license_plate}'")
                return False

        except Exception as e:
            # Capturar errores durante la eliminación (ej. errores de red, constraints de BD)
            logger.error(f"❌ Error al eliminar vehículo '{license_plate}': {e}", exc_info=True)
            return False

    def update_vehicle(self, license_plate: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """
        Actualiza un vehículo existente en la base de datos Supabase.

        Realiza pre-procesamiento de los datos similar a add_vehicle:
        - Convierte objetos `date` y `datetime` a strings en formato ISO 8601.
        - Convierte strings vacíos o compuestos solo de espacios en blanco a `None`.
        - Convierte Decimal a float.

        Args:
            license_plate: La patente del vehículo a actualizar.
            data: Un diccionario con los datos actualizados del vehículo.

        Returns:
            Un diccionario con los datos del vehículo actualizado si fue exitoso,
            o None si no se pudo actualizar.
        """
        try:
            logger.info(f"🔄 Intentando actualizar vehículo con patente: '{license_plate}'")
            
            # Verificar que el vehículo existe
            vehicle = self.get_vehicle(license_plate)
            if not vehicle:
                logger.warning(f"⚠️ No se puede actualizar: vehículo con patente '{license_plate}' no encontrado.")
                return None

            # Procesar los datos
            processed_data = {}
            
            for key, value in data.items():
                # Saltar campos que no se deben actualizar
                if key in ['id', 'license_plate']:
                    logger.debug(f"🗑️ Campo '{key}' será excluido de la actualización.")
                    continue
                
                # Convertir fechas/datetimes a string ISO
                if isinstance(value, (date, datetime)):
                    processed_data[key] = value.isoformat()
                    logger.debug(f"🔄 Campo '{key}' convertido a ISO format: {processed_data[key]}")
                # Convertir Decimal a float
                elif isinstance(value, Decimal):
                    processed_data[key] = float(value)
                    logger.debug(f"🔄 Campo '{key}' (Decimal) convertido a float: {processed_data[key]}")
                # Convertir strings vacíos a None
                elif isinstance(value, str) and not value.strip():
                    processed_data[key] = None
                    logger.debug(f"🔄 Campo string vacío '{key}' convertido a None.")
                else:
                    processed_data[key] = value

            # Actualizar en Supabase
            response = (
                self.client.table("vehicle")
                .update(processed_data)
                .eq("license_plate", license_plate)
                .execute()
            )
            
            logger.debug(f"📊 Respuesta cruda de Supabase (update_vehicle): {response.data}")

            # Verificar si la operación fue exitosa
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Vehículo actualizado exitosamente: {license_plate}")
                # Obtener los datos completos actualizados
                return self.get_vehicle(license_plate)
            else:
                logger.warning("⚠️ Supabase no devolvió datos después de la actualización.")
                return None

        except Exception as e:
            logger.error(f"❌ Error al actualizar vehículo '{license_plate}': {e}", exc_info=True)
            return None