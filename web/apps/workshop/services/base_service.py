import logging
from typing import Any, Dict, List, Optional
from accounts.client.supabase_client import get_supabase
from supabase import PostgrestAPIError

logger = logging.getLogger(__name__)


class WorkshopBaseService:
    """
    Clase base para los servicios de la app Workshop.
    
    Proporciona métodos comunes para interactuar con Supabase
    y filtrar datos por taller.
    """
    
    @staticmethod
    def get_client():
        """Obtiene el cliente de Supabase."""
        return get_supabase()
    
    @staticmethod
    def _execute_query(query, method_name: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta de Supabase y maneja los errores comunes.
        
        Args:
            query: La consulta de PostgREST a ejecutar.
            method_name: El nombre del método que llama para logging.
            
        Returns:
            Los datos de la respuesta o una lista vacía en caso de error.
        """
        try:
            response = query.execute()
            logger.debug(f"📊 ({method_name}) Respuesta de Supabase: {response.data}")
            return response.data if response.data is not None else []
        except PostgrestAPIError as e:
            logger.error(f"❌ ({method_name}) Error de API: {e.message}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"❌ ({method_name}) Error inesperado: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _execute_single(query, method_name: str) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta que espera un solo resultado.
        
        Args:
            query: La consulta de PostgREST a ejecutar.
            method_name: El nombre del método que llama para logging.
            
        Returns:
            Los datos del registro o None en caso de error.
        """
        try:
            response = query.maybe_single().execute()
            logger.debug(f"📊 ({method_name}) Respuesta de Supabase: {response.data}")
            return response.data
        except PostgrestAPIError as e:
            logger.error(f"❌ ({method_name}) Error de API: {e.message}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"❌ ({method_name}) Error inesperado: {e}", exc_info=True)
            return None


