import logging
from abc import ABC
from typing import Any, Dict, List
from accounts.client.supabase_client import get_supabase_with_user
from supabase import PostgrestAPIError

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)

class BaseService(ABC):
    """
    Clase Base Abstracta para servicios que interactúan con Supabase.

    Centraliza la inicialización del cliente Supabase y proporciona una
    interfaz común para los servicios de la aplicación, promoviendo la
    consistencia y reutilización de código.
    """

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.

        Args:
            token: El token de acceso JWT del usuario actual.
            refresh_token: El token de refresco del usuario actual.
        """
        self.client = get_supabase_with_user(token, refresh_token)
        logger.debug(f"🔧 Instancia de {self.__class__.__name__} creada.")

    def _execute_query(self, query, method_name: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta de Supabase y maneja los errores comunes.
        
        Ahora puede manejar respuestas que no son listas 
        (como .maybe_single()).

        Args:
            query: La consulta de PostgREST a ejecutar.
            method_name (str): El nombre del método que llama para logging.

        Returns:
            Los datos de la respuesta (lista, dict, o None) o una lista vacía 
            en caso de error.
        """
        try:
            response = query.execute()
            logger.debug(f"📊 ({method_name}) Respuesta cruda de Supabase: {response.data}")
            
            # .maybe_single() devuelve un dict directamente, no una lista.
            # Otros (select, insert, update) devuelven una lista.
            # Si no hay datos, 'response.data' puede ser [] o None.
            return response.data
        
        except PostgrestAPIError as e:
            logger.error(f"❌ ({method_name}) Error de API: {e.message}", exc_info=True)
            return [] # Devuelve lista vacía en error de API
        except Exception as e:
            logger.error(f"❌ ({method_name}) Error inesperado: {e}", exc_info=True)
            return [] # Devuelve lista vacía en error genérico
