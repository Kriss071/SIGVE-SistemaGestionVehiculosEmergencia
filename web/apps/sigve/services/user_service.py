import logging
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService

logger = logging.getLogger(__name__)


class UserService(SigveBaseService):
    """Servicio para gestionar usuarios de la plataforma."""
    
    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios de la plataforma.
        
        Returns:
            Lista de usuarios con su información de perfil.
        """
        client = SigveBaseService.get_client()
        query = client.table("user_profile") \
            .select("""
                *,
                role:role_id(name),
                workshop:workshop_id(name),
                fire_station:fire_station_id(name)
            """) \
            .order("first_name")
        
        return SigveBaseService._execute_query(query, "get_all_users")
    
    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario específico por ID.
        
        Args:
            user_id: UUID del usuario.
            
        Returns:
            Datos del usuario o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .select("""
                    *,
                    role:role_id(name),
                    workshop:workshop_id(name),
                    fire_station:fire_station_id(name)
                """) \
                .eq("id", user_id) \
                .maybe_single() \
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario {user_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def update_user(user_id: str, data: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: UUID del usuario.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .update(data) \
                .eq("id", user_id) \
                .execute()
            
            logger.info(f"✅ Usuario {user_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando usuario {user_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def deactivate_user(user_id: str) -> bool:
        """
        Desactiva un usuario (is_active = false).
        
        Args:
            user_id: UUID del usuario.
            
        Returns:
            True si se desactivó correctamente, False en caso contrario.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .update({"is_active": False}) \
                .eq("id", user_id) \
                .execute()
            
            logger.info(f"🚫 Usuario {user_id} desactivado")
            return True
        except Exception as e:
            logger.error(f"❌ Error desactivando usuario {user_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_all_roles() -> List[Dict[str, Any]]:
        """
        Obtiene todos los roles disponibles.
        
        Returns:
            Lista de roles.
        """
        client = SigveBaseService.get_client()
        query = client.table("role").select("*").order("name")
        return SigveBaseService._execute_query(query, "get_all_roles")
    
    @staticmethod
    def create_user_profile(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un perfil de usuario (después de crear la cuenta en auth.users).
        
        Args:
            user_data: Datos del perfil (id, first_name, last_name, rut, phone, role_id, etc.)
            
        Returns:
            Datos del perfil creado o None.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile").insert(user_data).execute()
            
            if result.data:
                logger.info(f"✅ Perfil de usuario creado: {user_data.get('first_name')} {user_data.get('last_name')}")
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as e:
            logger.error(f"❌ Error creando perfil de usuario: {e}", exc_info=True)
            return None


