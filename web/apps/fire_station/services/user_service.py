import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from supabase import PostgrestAPIError
from .base_service import FireStationBaseService
from accounts.client.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


class UserService(FireStationBaseService):
    """
    Servicio para la gestión de usuarios del cuartel.
    """
    
    @classmethod
    def get_all_users(cls, fire_station_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios del cuartel.
        
        Args:
            fire_station_id: ID del cuartel.
            
        Returns:
            Lista de usuarios.
        """
        logger.info(f"👥 Obteniendo usuarios para cuartel {fire_station_id}")
        
        client = cls.get_client()
        
        users = cls._execute_query(
            client.table('user_profile')
                .select('*, role(id, name)')
                .eq('fire_station_id', fire_station_id)
                .order('first_name'),
            'get_all_users'
        )
        
        # Obtener emails de auth.users para cada usuario
        for user in users:
            user_id = user.get('id')
            if user_id:
                auth_user = cls.get_user_auth_data(user_id)
                if auth_user:
                    user['email'] = auth_user.get('email')
        
        return users
    
    @classmethod
    def get_user(cls, user_id: str, fire_station_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario (UUID).
            fire_station_id: ID del cuartel (opcional, para validación).
            
        Returns:
            Datos del usuario o None si no existe.
        """
        logger.info(f"👤 Obteniendo usuario {user_id}")
        
        client = cls.get_client()
        
        query = client.table('user_profile').select(
            '*, role(id, name), fire_station(id, name)'
        ).eq('id', user_id)
        
        if fire_station_id:
            query = query.eq('fire_station_id', fire_station_id)
        
        user = cls._execute_single(query, 'get_user')
        
        if user:
            # Obtener email del usuario de auth
            auth_user = cls.get_user_auth_data(user_id)
            if auth_user:
                user['email'] = auth_user.get('email')
        
        return user
    
    @classmethod
    def get_user_auth_data(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de autenticación de un usuario.
        
        Args:
            user_id: ID del usuario (UUID).
            
        Returns:
            Datos de auth.users o None.
        """
        try:
            admin_client = get_supabase_admin()
            response = admin_client.auth.admin.get_user_by_id(user_id)
            return response.user.model_dump() if response.user else None
        except Exception as e:
            logger.error(f"❌ Error al obtener datos de auth para usuario {user_id}: {e}")
            return None
    
    @staticmethod
    def _parse_duplicate_error(error: Exception) -> Optional[Dict[str, str]]:
        """
        Parsea un error de Supabase para identificar qué campo está duplicado en user_profile.
        
        Args:
            error: La excepción capturada.
            
        Returns:
            Diccionario con el campo duplicado y mensaje, o None si no es un error de duplicación.
        """
        error_msg = str(error).lower()
        error_details = getattr(error, 'message', '') or error_msg
        
        # Mapeo de campos y sus mensajes de error
        field_mapping = {
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
            return {
                'field': 'general',
                'message': 'Ya existe un registro con estos datos. Verifica que los datos sean únicos.'
            }
        
        return None
    
    @classmethod
    def update_user(cls, user_id: str, fire_station_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Actualiza un usuario del cuartel.
        
        Args:
            user_id: ID del usuario.
            fire_station_id: ID del cuartel (para validación).
            data: Datos a actualizar.
            
        Returns:
            Tupla (éxito, errores). Si hay errores, el primer elemento es False.
        """
        logger.info(f"✏️ Actualizando usuario {user_id}")
        
        client = cls.get_client()
        
        # Agregar timestamp de actualización
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Convertir cadenas vacías a None para campos opcionales
        for key in ['rut', 'phone']:
            if key in data and data[key] == '':
                data[key] = None
        
        try:
            # Ejecutar directamente para capturar excepciones de duplicado
            response = client.table('user_profile') \
                .update(data) \
                .eq('id', user_id) \
                .eq('fire_station_id', fire_station_id) \
                .execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Usuario {user_id} actualizado correctamente")
                return True, None
            else:
                logger.error(f"❌ Error al actualizar usuario {user_id}: respuesta vacía")
                return False, {'general': ['Error al actualizar el usuario. Por favor, intenta nuevamente.']}
        except PostgrestAPIError as e:
            logger.error(f"❌ Error de API actualizando usuario {user_id}: {e.message}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            return False, {'general': ['Error al actualizar el usuario. Por favor, intenta nuevamente.']}
        except Exception as e:
            logger.error(f"❌ Error inesperado actualizando usuario {user_id}: {e}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(e)
            if duplicate_error:
                return False, {duplicate_error['field']: [duplicate_error['message']]}
            
            return False, {'general': ['Error al actualizar el usuario. Por favor, intenta nuevamente.']}
    
    @classmethod
    def deactivate_user(cls, user_id: str, fire_station_id: int) -> bool:
        """
        Desactiva un usuario del cuartel.
        
        Args:
            user_id: ID del usuario.
            fire_station_id: ID del cuartel (para validación).
            
        Returns:
            True si se desactivó correctamente, False en caso contrario.
        """
        return cls.update_user(user_id, fire_station_id, {'is_active': False})
    
    @classmethod
    def activate_user(cls, user_id: str, fire_station_id: int) -> bool:
        """
        Activa un usuario del cuartel.
        
        Args:
            user_id: ID del usuario.
            fire_station_id: ID del cuartel (para validación).
            
        Returns:
            True si se activó correctamente, False en caso contrario.
        """
        return cls.update_user(user_id, fire_station_id, {'is_active': True})
    
    @classmethod
    def delete_user(cls, user_id: str, fire_station_id: int) -> bool:
        """
        Elimina un usuario del cuartel (tanto de auth.users como de user_profile).
        
        Args:
            user_id: ID del usuario.
            fire_station_id: ID del cuartel (para validación).
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        logger.info(f"🗑️ Eliminando usuario {user_id}")
        
        client = cls.get_client()
        admin_client = get_supabase_admin()
        
        try:
            # Paso 1: Verificar que el usuario existe y pertenece al cuartel
            user = cls.get_user(user_id, fire_station_id)
            if not user:
                logger.warning(f"⚠️ Usuario {user_id} no encontrado o no pertenece al cuartel {fire_station_id}")
                return False
            
            # Paso 2: Eliminar perfil de user_profile
            result = client.table('user_profile') \
                .delete() \
                .eq('id', user_id) \
                .eq('fire_station_id', fire_station_id) \
                .execute()
            
            if not result.data:
                logger.warning(f"⚠️ No se pudo eliminar el perfil del usuario {user_id}")
                return False
            
            # Paso 3: Eliminar usuario de auth.users
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info(f"✅ Usuario {user_id} eliminado de auth")
            except Exception as auth_error:
                logger.error(f"⚠️ Error eliminando usuario {user_id} de auth: {auth_error}", exc_info=True)
                # Continuar aunque falle la eliminación de auth, el perfil ya se eliminó
            
            logger.info(f"✅ Usuario {user_id} eliminado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando usuario {user_id}: {e}", exc_info=True)
            return False
    
    @classmethod
    def get_all_roles(cls) -> List[Dict[str, Any]]:
        """Obtiene todos los roles disponibles."""
        client = cls.get_client()
        return cls._execute_query(
            client.table('role').select('*').order('name'),
            'get_all_roles'
        )
    
    @classmethod
    def get_fire_station_roles(cls) -> List[Dict[str, Any]]:
        """
        Obtiene los roles específicos para usuarios de cuartel.
        Típicamente: Jefe Cuartel, Conductor, etc.
        """
        client = cls.get_client()
        # Filtrar roles que son apropiados para cuarteles
        all_roles = cls.get_all_roles()
        # Excluir roles de Admin SIGVE, Admin Taller y Mecánico
        excluded_roles = ['Admin SIGVE', 'Admin Taller', 'Mecánico']
        return [role for role in all_roles if role.get('name') not in excluded_roles]
    
    @classmethod
    def create_user(
        cls,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role_id: int,
        fire_station_id: int,
        rut: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo usuario del cuartel.
        
        Args:
            email: Correo electrónico del usuario
            password: Contraseña del usuario
            first_name: Nombre del usuario
            last_name: Apellido del usuario
            role_id: ID del rol (debe ser un rol válido para cuartel)
            fire_station_id: ID del cuartel
            rut: RUT del usuario (opcional)
            phone: Teléfono del usuario (opcional)
            
        Returns:
            Dict con success, user_id, y error (si aplica)
        """
        admin_client = get_supabase_admin()
        
        try:
            # Paso 1: Crear usuario en auth.users
            response = admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "first_name": first_name,
                    "last_name": last_name
                }
            })
            
            auth_user = getattr(response, "user", None)
            if not auth_user:
                logger.error("❌ Supabase no retornó usuario en la respuesta.")
                return {"success": False, "user_id": None, "error": "No se pudo crear el usuario."}
            
            user_id = getattr(auth_user, "id", None)
            if not user_id:
                logger.error("❌ No se obtuvo el ID del usuario creado.")
                return {"success": False, "user_id": None, "error": "No se obtuvo el ID del usuario."}
            
        except Exception as auth_error:
            logger.error(f"❌ Error creando usuario en auth: {auth_error}", exc_info=True)
            error_msg = str(auth_error).lower()
            if "already registered" in error_msg or "duplicate" in error_msg or "email" in error_msg:
                return {"success": False, "user_id": None, "error": "El correo electrónico ya está registrado.", "error_field": "email"}
            return {"success": False, "user_id": None, "error": "Error creando el usuario.", "error_field": None}
        
        # Paso 2: Crear perfil en user_profile
        try:
            client = cls.get_client()
            profile_data = {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "rut": rut,
                "phone": phone,
                "role_id": role_id,
                "fire_station_id": fire_station_id,
                "is_active": True
            }
            
            result = client.table("user_profile") \
                .insert(profile_data) \
                .execute()
            
            if not result.data:
                raise Exception("No se pudo crear el perfil del usuario.")
            
            logger.info(f"✅ Usuario {email} creado correctamente con ID {user_id}")
            return {"success": True, "user_id": user_id, "error": None, "error_field": None}
            
        except Exception as profile_error:
            logger.error(f"❌ Error creando perfil del usuario: {profile_error}", exc_info=True)
            
            # Intentar parsear error de duplicación
            duplicate_error = cls._parse_duplicate_error(profile_error)
            error_message = "Error creando el perfil del usuario."
            error_field = None
            if duplicate_error:
                error_message = duplicate_error['message']
                error_field = duplicate_error['field']
            
            # Revertir: eliminar usuario de auth
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info(f"♻️ Usuario {user_id} eliminado de auth tras error en perfil.")
            except Exception as cleanup_error:
                logger.error(f"⚠️ Error al revertir usuario en auth: {cleanup_error}", exc_info=True)
            
            return {"success": False, "user_id": user_id, "error": error_message, "error_field": error_field}

