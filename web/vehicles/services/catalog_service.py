import logging
from typing import List, Dict, Any
from accounts.client.supabase_client import get_supabase


# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)


class CatalogService:
    """
    Servicio para obtener datos de las tablas de catálogo (lookup tables).

    Proporciona métodos estáticos para recuperar opciones que se utilizarán
    en formularios y vistas, como listas de cuarteles, tipos de vehículos, etc.
    Cada método se conecta a Supabase y obtiene los registros de una tabla específica.
    """

    @staticmethod
    def _fetch_catalog(table_name: str, columns: str = "id, name") -> List[Dict[str, Any]]:
        """
        Método auxiliar genérico para obtener datos de una tabla de catálogo.

        Args:
            table_name (str): El nombre de la tabla de Supabase.
            columns (str): Las columnas a seleccionar.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios o una lista vacía en caso de error.
        """
        logger.debug(f"📚 (fetch_catalog) Obteniendo catálogo: '{table_name}'...")
        try:
            supabase = get_supabase()
            response = supabase.table(table_name).select(columns).order("name").execute()
            logger.info(f"✅ (fetch_catalog) Catálogo '{table_name}' obtenido con {len(response.data)} registros.")
            # Devuelve los datos si existen, o una lista vacía si la respuesta es vacía o None.
            return response.data or []
        except Exception as e:
            logger.error(f"❌ (fetch_catalog) Error al obtener el catálogo '{table_name}': {e}", exc_info=True)
            return []

    @staticmethod
    def get_fire_stations() -> List[Dict[str, Any]]:
        """Obtiene todas las estaciones de bomberos ordenadas por nombre."""
        return CatalogService._fetch_catalog("fire_station", "id, name, address")

    @staticmethod
    def get_vehicle_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de vehículos ordenados por nombre."""
        return CatalogService._fetch_catalog("vehicle_type", "id, name, description")

    @staticmethod
    def get_vehicle_statuses() -> List[Dict[str, Any]]:
        """Obtiene todos los estados de vehículos ordenados por nombre."""
        return CatalogService._fetch_catalog("vehicle_status", "id, name, description")

    @staticmethod
    def get_fuel_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de combustible ordenados por nombre."""
        return CatalogService._fetch_catalog("fuel_type")

    @staticmethod
    def get_transmission_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de transmisión ordenados por nombre."""
        return CatalogService._fetch_catalog("transmission_type")

    @staticmethod
    def get_oil_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de aceite ordenados por nombre."""
        return CatalogService._fetch_catalog("oil_type", "id, name, description")

    @staticmethod
    def get_coolant_types() -> List[Dict[str, Any]]:
        """Obtiene todos los tipos de refrigerante ordenados por nombre."""
        return CatalogService._fetch_catalog("coolant_type", "id, name, description")

