import logging
from typing import Dict, List, Any, Optional
from .base_service import SigveBaseService
from supabase import Client

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
        Desactiva un usuario (soft delete) en la tabla user_profile.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .update({'is_active': False}) \
                .eq("id", user_id) \
                .execute()
            
            if result.data:
                logger.info(f"🚫 Usuario {user_id} desactivado")
                return True
            logger.warning(f"⚠️ No se pudo desactivar el usuario {user_id}, no se encontró.")
            return False
        except Exception as e:
            logger.error(f"❌ Error desactivando usuario {user_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def activate_user(user_id: str) -> bool:
        """
        Activa un usuario en la tabla user_profile.
        
        Args:
            user_id: ID (UUID) del usuario.
            
        Returns:
            True si se actualizó, False si no.
        """
        client = SigveBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .update({'is_active': True}) \
                .eq("id", user_id) \
                .execute()
            
            if result.data:
                logger.info(f"✅ Usuario {user_id} activado")
                return True
            logger.warning(f"⚠️ No se pudo activar el usuario {user_id}, no se encontró.")
            return False
        except Exception as e:
            logger.error(f"❌ Error activando usuario {user_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Elimina permanentemente a un usuario del sistema (supabase.auth).
        La tabla user_profile debería borrarse en cascada.
        
        Args:
            user_id: ID (UUID) del usuario.
            
        Returns:
            True si se eliminó, False si no.
        """

        admin_client: Client = SigveBaseService.get_admin_client()        

        try:
            # Esta es la llamada a la API de admin de Supabase
            admin_client.auth.admin.delete_user(user_id)
            
            logger.info(f"🗑️ Usuario {user_id} eliminado permanentemente de auth.")
            return True
        except Exception as e:
            # Captura errores, por ej. si el usuario no existe en auth
            logger.error(f"❌ Error eliminando permanentemente al usuario {user_id}: {e}", exc_info=True)
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

    @staticmethod
    def create_user(
        *,
        email: str,
        password: str,
        profile_data: Dict[str, Any],
        email_confirm: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea un usuario en auth.users y su perfil asociado en user_profile.

        Args:
            email: Correo electrónico del usuario.
            password: Contraseña inicial.
            profile_data: Datos para la tabla user_profile (sin el ID).
            email_confirm: Marca si el correo queda confirmado automáticamente.
            metadata: Metadatos adicionales para auth.users.

        Returns:
            Diccionario con claves:
                success (bool)
                user_id (str | None)
                error (str | None)
        """
        admin_client: Client = SigveBaseService.get_admin_client()
        metadata = metadata or {}

        try:
            response = admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": email_confirm,
                "user_metadata": metadata
            })

            auth_user = getattr(response, "user", None)
            if not auth_user:
                logger.error("❌ (create_user) Supabase no retornó usuario en la respuesta.")
                return {"success": False, "user_id": None, "error": "Supabase no retornó el usuario creado."}

            user_id = getattr(auth_user, "id", None)
            if not user_id:
                logger.error("❌ (create_user) No se obtuvo el ID del usuario creado en auth.")
                return {"success": False, "user_id": None, "error": "No se obtuvo el ID del usuario creado en auth."}

        except Exception as auth_error:
            logger.error(f"❌ Error creando usuario en auth.users: {auth_error}", exc_info=True)
            return {"success": False, "user_id": None, "error": "Error creando el usuario en Supabase Auth."}

        profile_payload = {
            **profile_data,
            "id": user_id
        }

        created_profile = UserService.create_user_profile(profile_payload)
        if not created_profile:
            logger.error("❌ (create_user) No se pudo crear el perfil, revirtiendo usuario en auth.")
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info("♻️ (create_user) Usuario en auth eliminado tras fallo en user_profile.")
            except Exception as cleanup_error:
                logger.error(f"⚠️ (create_user) Fallo al revertir usuario en auth: {cleanup_error}", exc_info=True)

            return {"success": False, "user_id": user_id, "error": "Error creando el perfil del usuario."}

        logger.info(f"✅ Usuario creado correctamente con ID {user_id}")
        return {"success": True, "user_id": user_id, "error": None}


