import logging
from typing import Any, List, Dict
from accounts.client.supabase_client import get_supabase_with_user
from supabase import PostgrestAPIError


# Configura el logger para este módulo
logger = logging.getLogger(__name__)


class SupabaseRoleService:
    """
    Implementación del servicio de gestión de Roles utilizando Supabase.
    Interactúa con la tabla 'role'.
    """

    TABLE_NAME = "role"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        self.client = get_supabase_with_user(token, refresh_token)
        logger.debug(f"🔧 Instancia de SupabaseRoleService creada para la tabla '{self.TABLE_NAME}'.")


    def list_roles(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los roles ordenados por nombre.
        """
        logger.info(f"📄 (list_roles) Obteniendo todos los roles de la tabla '{self.TABLE_NAME}'.")
        try:
            response = self.client.table(self.TABLE_NAME).select("*").order("name").execute()
            logger.debug(f"📊 (list_roles) Respuesta de Supabase: {len(response.data)} roles encontrados.")
            return response.data or []
        except PostgrestAPIError as e:
            logger.error(f"❌ (list_roles) Error de API al listar roles: {e.message}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"❌ (list_roles) Error inesperado al listar roles: {e}", exc_info=True)
            return []

 