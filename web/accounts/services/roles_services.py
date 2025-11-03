import logging
from time import process_time_ns
from urllib import request
from ..client.supabase_client import get_supabase

logger = logging.getLogger(__name__) 

class RolesService:
    """
    Clase de servicio que encapsula la lógica de negocio para la gestión 
    de roles de usuarios (user_profile) interactuando con Supabase.
    
    Todos los métodos son estáticos (@staticmethod) ya que no se requiere 
    almacenar estado en la instancia de la clase.
    """

    @staticmethod
    def get_user_role(user_id: str):
        """
        Obtiene el nombre del rol de un usuario a partir de su ID.

        Realiza una consulta a la tabla 'user_profile' y utiliza una relación 
        (join implícito de Supabase) con la tabla 'role' para obtener el 
        nombre descriptivo del rol.

        Args:
            user_id (str): El UUID del usuario a consultar.

        Returns:
            (str | None): El nombre del rol como un string (ej. "Admin SIGVE") si se encuentra.
                         Retorna None si el usuario no existe, no tiene rol 
                         asignado, o si ocurre un error.
        """

        supabase = get_supabase()
        logger.info(f"ℹ️ Buscando rol para el usuario ID: {user_id}")

        try:
            # La sintaxis 'role:role_id(name)' le indica a Supabase que:
            # 1. Use la columna 'role_id' de la tabla 'user_profile'.
            # 2. Busque la coincidencia en la tabla 'role'.
            # 3. Devuelva la columna 'name' de esa tabla 'role'.
            # 4. Anide el resultado bajo la clave 'role'.
            result = (
                supabase.table("user_profile")
                .select("id, role:role_id(name)")
                .eq("id", user_id)
                .execute()
            )

            logger.debug(f"🐛 Resultado de Supabase (get_user_role): {result.data}")

            if result.data:
                user = result.data[0]
                role_info = user.get('role')

                logger.debug(f"🐛 Resultado role_info: {role_info}")

                # Se espera que 'role_info' sea un diccionario, ej: {'name': 'Admin SIGVE'}
                if isinstance(role_info, dict):
                    role_name = role_info.get('name')
                    if role_name:
                        logger.info(f"✅ Rol encontrado para {user_id}: {role_name}")
                        return role_name
            
                # Si el usuario existe pero 'role' es None o no es un dict
                logger.warning(f"⚠️ Usuario {user_id} encontrado, pero sin relación de rol válida.")
            else:
                logger.warning(f"⚠️ Usuario no encontrado en la tabla 'user_profile': {user_id}")
               
        except Exception as e:
            # 'exc_info=True' incluye el traceback completo en el log de error.
            logger.error(f"❌ Error al obtener rol del usuario {user_id}: {e}", exc_info=True)
                 
        return None


# REVISAR -----------------

    @staticmethod
    def get_role_id(user_id: str):
        """
        Obtiene el ID del rol de un usuario.
        
        Args:
            user_id (str): El UUID del usuario a consultar.
            
        Returns:
            (int | None): El ID del rol si se encuentra, None en caso contrario.
        """
        supabase = get_supabase()
        try:
            result = (
                supabase.table("user_profile")
                .select("role_id")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )

            if result.data:
                logger.info(f"✅ role_id encontrado para usuario {user_id}: {result.data.get('role_id')}")
                return result.data.get('role_id')
            
            logger.warning(f"⚠️ No se encontró role_id para usuario {user_id}")
        except Exception as e:
            logger.error(f"❌ Error al obtener role_id del usuario {user_id}: {e}", exc_info=True)
        
        return None

    @staticmethod
    def set_user_role(user_id: str, role_name: str):
        """
        Actualiza el rol de un usuario buscando el role_id por nombre.
        
        Args:
            user_id (str): El UUID del usuario a actualizar.
            role_name (str): El nombre del rol a asignar.
            
        Returns:
            (bool): True si la actualización fue exitosa, False en caso contrario.
        """
        supabase = get_supabase()
        
        try:
            # Buscar el role_id por nombre
            role_result = (
                supabase.table("role")
                .select("id")
                .eq("name", role_name)
                .maybe_single()
                .execute()
            )
            
            if not role_result.data:
                logger.warning(f"⚠️ Rol '{role_name}' no encontrado")
                return False
            
            role_id = role_result.data['id']
            
            # Actualizar el user_profile con el nuevo role_id
            result = (
                supabase.table("user_profile")
                .update({"role_id": role_id})
                .eq("id", user_id)
                .execute()
            )
            
            if result.data:
                logger.info(f"✅ Rol actualizado para usuario {user_id}: {role_name}")
                return True
            
            logger.warning(f"⚠️ No se pudo actualizar el rol para usuario {user_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Error al actualizar rol del usuario {user_id}: {e}", exc_info=True)
            return False
