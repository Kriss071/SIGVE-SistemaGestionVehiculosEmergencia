import logging
from typing import Dict, List, Any, Optional, Iterable, Tuple
from .base_service import SigveBaseService
from supabase import Client, PostgrestAPIError

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
        
        users = SigveBaseService._execute_query(query, "get_all_users")
        return UserService._attach_auth_user_data(users)
    
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
            
            user = result.data
            if user:
                enriched = UserService._attach_auth_user_data([user])
                return enriched[0] if enriched else user
            return user
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario {user_id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _parse_duplicate_error_user(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado en usuarios.
        
        Args:
            error: La excepción capturada.
            
        Returns:
            Diccionario con el campo duplicado y mensaje, o None si no es un error de duplicación.
        """
        error_msg = str(error).lower()
        error_details = getattr(error, 'message', '') or error_msg
        
        # Mapeo de campos y sus mensajes de error
        field_mapping = {
            'email': {
                'keywords': ['email', 'correo', 'e-mail', 'user already registered'],
                'message': 'Este correo electrónico ya está registrado en otro usuario.'
            },
            'rut': {
                'keywords': ['rut'],
                'message': 'Este RUT ya está registrado en otro usuario.'
            },
            'phone': {
                'keywords': ['phone', 'teléfono', 'telefono'],
                'message': 'Este número de teléfono ya está registrado en otro usuario.'
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
                if 'email' in constraint_name or 'user_email' in constraint_name:
                    return {'field': 'email', 'message': field_mapping['email']['message']}
                elif 'rut' in constraint_name:
                    return {'field': 'rut', 'message': field_mapping['rut']['message']}
                elif 'phone' in constraint_name:
                    return {'field': 'phone', 'message': field_mapping['phone']['message']}
            
            # Si no se puede identificar, retornar un error genérico
            return {
                'field': 'general',
                'message': 'Ya existe un usuario con estos datos. Verifica que el correo, RUT y teléfono sean únicos.'
            }
        
        return None
    
    @staticmethod
    def check_duplicates_user(email: Optional[str] = None, profile_data: Optional[Dict[str, Any]] = None, exclude_user_id: Optional[str] = None) -> Dict[str, str]:
        """
        Verifica si hay duplicados antes de crear/actualizar un usuario.
        
        Args:
            email: Correo electrónico a verificar (en auth.users).
            profile_data: Datos del perfil a verificar (rut, phone en user_profile).
            exclude_user_id: ID del usuario a excluir de la verificación (para edición).
            
        Returns:
            Diccionario con errores por campo si hay duplicados, vacío si no hay.
        """
        errors = {}
        admin_client: Optional[Client] = None
        client = SigveBaseService.get_client()
        
        # Verificar email duplicado en auth.users
        if email:
            try:
                admin_client = SigveBaseService.get_admin_client()
                # Intentar obtener usuario por email
                try:
                    response = admin_client.auth.admin.list_users()
                    users = getattr(response, 'users', [])
                    
                    for user in users:
                        user_email = getattr(user, 'email', None) or (user.get('email') if isinstance(user, dict) else None)
                        user_id = getattr(user, 'id', None) or (user.get('id') if isinstance(user, dict) else None)
                        
                        if user_email and user_email.lower() == email.lower():
                            if not exclude_user_id or user_id != exclude_user_id:
                                errors['email'] = 'Este correo electrónico ya está registrado en otro usuario.'
                                break
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo verificar email duplicado: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo admin client para verificar email: {e}")
        
        # Verificar RUT duplicado en user_profile (solo si se proporciona y no es None o vacío)
        if profile_data and profile_data.get('rut'):
            rut_value = profile_data['rut']
            if rut_value and isinstance(rut_value, str) and rut_value.strip():
                try:
                    query = client.table("user_profile").select("id, first_name, last_name").eq("rut", rut_value.strip())
                    if exclude_user_id:
                        query = query.neq("id", exclude_user_id)
                    existing = query.execute()
                    if existing.data and len(existing.data) > 0:
                        errors['rut'] = 'Este RUT ya está registrado en otro usuario.'
                except Exception as e:
                    logger.warning(f"⚠️ Error verificando RUT duplicado: {e}")
        
        # Verificar teléfono duplicado en user_profile (solo si se proporciona y no es None o vacío)
        if profile_data and profile_data.get('phone'):
            phone_value = profile_data['phone']
            if phone_value and isinstance(phone_value, str) and phone_value.strip():
                try:
                    query = client.table("user_profile").select("id, first_name, last_name").eq("phone", phone_value.strip())
                    if exclude_user_id:
                        query = query.neq("id", exclude_user_id)
                    existing = query.execute()
                    if existing.data and len(existing.data) > 0:
                        errors['phone'] = 'Este número de teléfono ya está registrado en otro usuario.'
                except Exception as e:
                    logger.warning(f"⚠️ Error verificando teléfono duplicado: {e}")
        
        return errors
    
    @staticmethod
    def update_user(user_id: str, profile_data: Dict[str, Any], *, email: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: UUID del usuario.
            profile_data: Datos a actualizar en user_profile.
            email: Nuevo correo electrónico (se actualiza en auth.users).
            
        Returns:
            Tupla (éxito, errores):
            - éxito: True si se actualizó correctamente, False en caso contrario.
            - errores: Diccionario con errores por campo si hay duplicados, None si no hay errores.
        """
        client = SigveBaseService.get_client()
        admin_client: Optional[Client] = None

        # Verificar duplicados antes de intentar actualizar
        duplicate_errors = UserService.check_duplicates_user(
            email=email,
            profile_data=profile_data,
            exclude_user_id=user_id
        )
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de actualizar usuario {user_id} con datos duplicados: {duplicate_errors}")
            return False, duplicate_errors

        if email is not None:
            try:
                admin_client = SigveBaseService.get_admin_client()
                admin_client.auth.admin.update_user_by_id(user_id, {"email": email})
                logger.info(f"📧 Email actualizado para usuario {user_id}")
            except Exception as auth_error:
                logger.error(f"❌ Error actualizando email del usuario {user_id}: {auth_error}", exc_info=True)
                # Intentar parsear el error de duplicación
                duplicate_error = UserService._parse_duplicate_error_user(auth_error)
                if duplicate_error:
                    return False, {duplicate_error['field']: duplicate_error['message']}
                return False, {'email': ['Error al actualizar el correo electrónico.']}

        try:
            result = client.table("user_profile") \
                .update(profile_data) \
                .eq("id", user_id) \
                .execute()
            
            logger.info(f"✅ Usuario {user_id} actualizado")
            return True, None
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando usuario {user_id}: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = UserService._parse_duplicate_error_user(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el usuario. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error actualizando usuario {user_id}: {e}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = UserService._parse_duplicate_error_user(e)
            if duplicate_error:
                return False, {duplicate_error['field']: duplicate_error['message']}
            return False, {'general': ['Error al actualizar el usuario. Por favor, intenta nuevamente.']}
    
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
                errors (Dict[str, str] | None) - Errores de validación por campo
        """
        admin_client: Client = SigveBaseService.get_admin_client()
        metadata = metadata or {}

        # Verificar duplicados antes de intentar crear
        duplicate_errors = UserService.check_duplicates_user(
            email=email,
            profile_data=profile_data
        )
        if duplicate_errors:
            logger.warning(f"⚠️ Intento de crear usuario con datos duplicados: {duplicate_errors}")
            return {
                "success": False,
                "user_id": None,
                "error": "Error de validación: datos duplicados.",
                "errors": duplicate_errors
            }

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
                return {"success": False, "user_id": None, "error": "Supabase no retornó el usuario creado.", "errors": None}

            user_id = getattr(auth_user, "id", None)
            if not user_id:
                logger.error("❌ (create_user) No se obtuvo el ID del usuario creado en auth.")
                return {"success": False, "user_id": None, "error": "No se obtuvo el ID del usuario creado en auth.", "errors": None}

        except Exception as auth_error:
            logger.error(f"❌ Error creando usuario en auth.users: {auth_error}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = UserService._parse_duplicate_error_user(auth_error)
            if duplicate_error:
                return {
                    "success": False,
                    "user_id": None,
                    "error": "Error creando el usuario en Supabase Auth.",
                    "errors": {duplicate_error['field']: duplicate_error['message']}
                }
            return {"success": False, "user_id": None, "error": "Error creando el usuario en Supabase Auth.", "errors": None}

        profile_payload = {
            **profile_data,
            "id": user_id
        }

        try:
            created_profile = UserService.create_user_profile(profile_payload)
            if not created_profile:
                logger.error("❌ (create_user) No se pudo crear el perfil, revirtiendo usuario en auth.")
                try:
                    admin_client.auth.admin.delete_user(user_id)
                    logger.info("♻️ (create_user) Usuario en auth eliminado tras fallo en user_profile.")
                except Exception as cleanup_error:
                    logger.error(f"⚠️ (create_user) Fallo al revertir usuario en auth: {cleanup_error}", exc_info=True)

                return {"success": False, "user_id": user_id, "error": "Error creando el perfil del usuario.", "errors": None}
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API creando perfil de usuario: {e.message}", exc_info=True)
            # Intentar parsear el error de duplicación
            duplicate_error = UserService._parse_duplicate_error_user(e)
            # Revertir usuario en auth
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info("♻️ (create_user) Usuario en auth eliminado tras fallo en user_profile.")
            except Exception as cleanup_error:
                logger.error(f"⚠️ (create_user) Fallo al revertir usuario en auth: {cleanup_error}", exc_info=True)
            
            if duplicate_error:
                return {
                    "success": False,
                    "user_id": user_id,
                    "error": "Error creando el perfil del usuario.",
                    "errors": {duplicate_error['field']: duplicate_error['message']}
                }
            return {"success": False, "user_id": user_id, "error": "Error creando el perfil del usuario.", "errors": None}
        except Exception as e:
            logger.error(f"❌ Error creando perfil de usuario: {e}", exc_info=True)
            # Revertir usuario en auth
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info("♻️ (create_user) Usuario en auth eliminado tras fallo en user_profile.")
            except Exception as cleanup_error:
                logger.error(f"⚠️ (create_user) Fallo al revertir usuario en auth: {cleanup_error}", exc_info=True)
            
            # Intentar parsear el error de duplicación
            duplicate_error = UserService._parse_duplicate_error_user(e)
            if duplicate_error:
                return {
                    "success": False,
                    "user_id": user_id,
                    "error": "Error creando el perfil del usuario.",
                    "errors": {duplicate_error['field']: duplicate_error['message']}
                }
            return {"success": False, "user_id": user_id, "error": "Error creando el perfil del usuario.", "errors": None}

        logger.info(f"✅ Usuario creado correctamente con ID {user_id}")
        return {"success": True, "user_id": user_id, "error": None, "errors": None}

    @staticmethod
    def _attach_auth_user_data(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adjunta la información proveniente de auth.users (como el email)
        a los registros de user_profile.
        """
        if not users:
            return []

        ids = [user.get("id") for user in users if user.get("id")]
        auth_users = UserService._get_auth_users_by_ids(ids)

        for user in users:
            user_id = user.get("id")
            auth_data = auth_users.get(user_id, {})
            if auth_data:
                user["email"] = auth_data.get("email")
                user.setdefault("auth_user", auth_data)
        return users

    @staticmethod
    def _get_auth_users_by_ids(user_ids: Iterable[str]) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene los usuarios desde auth.users dada una lista de IDs.
        """
        unique_ids = list({uid for uid in user_ids if uid})
        if not unique_ids:
            return {}

        admin_client: Client = SigveBaseService.get_admin_client()
        auth_users: Dict[str, Dict[str, Any]] = {}

        for user_id in unique_ids:
            try:
                response = admin_client.auth.admin.get_user_by_id(user_id)
                auth_user = getattr(response, "user", None)
                if not auth_user:
                    continue

                email = getattr(auth_user, "email", None)
                if email is None and isinstance(auth_user, dict):
                    email = auth_user.get("email")

                phone = getattr(auth_user, "phone", None)
                if phone is None and isinstance(auth_user, dict):
                    phone = auth_user.get("phone")

                auth_users[user_id] = {
                    "email": email,
                    "phone": phone
                }
            except Exception as e:
                logger.warning(f"⚠️ No se pudo obtener auth.users para {user_id}: {e}")

        return auth_users


