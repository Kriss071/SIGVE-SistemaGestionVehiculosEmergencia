import logging
from typing import Any, List, Dict, Optional, Tuple
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError


# Configura el logger para este módulo
logger = logging.getLogger(__name__)


class SupabaseRoleService(BaseService):
    """
    Implementación del servicio de gestión de Roles utilizando Supabase.
    Interactúa con la tabla 'role'.
    """

    TABLE_NAME = "role"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de SupabaseRoleService creada para la tabla '{self.TABLE_NAME}'.")


    def list_roles(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los roles ordenados por nombre.
        """
        logger.info(f"📄 (list_roles) Obteniendo todos los roles de la tabla '{self.TABLE_NAME}'.")
        query = self.client.table(self.TABLE_NAME).select("*").order("name")
        return self._execute_query(query, "list_roles")
