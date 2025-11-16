import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
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
    
    @classmethod
    def update_user(cls, user_id: str, fire_station_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario del cuartel.
        
        Args:
            user_id: ID del usuario.
            fire_station_id: ID del cuartel (para validación).
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        logger.info(f"✏️ Actualizando usuario {user_id}")
        
        client = cls.get_client()
        
        # Agregar timestamp de actualización
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Actualizar perfil
        result = cls._execute_single(
            client.table('user_profile')
                .update(data)
                .eq('id', user_id)
                .eq('fire_station_id', fire_station_id),
            'update_user'
        )
        
        if result:
            logger.info(f"✅ Usuario {user_id} actualizado correctamente")
            return True
        else:
            logger.error(f"❌ Error al actualizar usuario {user_id}")
            return False
    
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

