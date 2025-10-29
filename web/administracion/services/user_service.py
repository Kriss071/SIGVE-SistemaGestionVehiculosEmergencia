# En: web/administracion/services/user_service.py
import logging
from accounts.client.supabase_client import get_supabase

logger = logging.getLogger(__name__)

class UserService:

    def list_users_with_roles(self):
        """Lista empleados desde la tabla 'employee' con el nombre de su rol."""
        supabase = get_supabase()
        logger.info("👥 Listando empleados con roles...")

        try:
            response = (
                supabase.table("employee")
                .select(
                    """
                    id, 
                    first_name, 
                    last_name, 
                    rut, 
                    phone, 
                    is_active,
                    role:role_id(name), 
                    workshop:workshop_id(name) 
                    """
                )
                .order("last_name")
                .execute()
            )

            logger.debug(f"📊 Respuesta cruda de Supabase (list_users_with_roles): {response.data}")

            if response.data is not None:
                users_list = []
                for user_data in response.data:
                    normalized_user = {
                        'id': user_data.get('id'),
                        'first_name': user_data.get('first_name', ''),
                        'last_name': user_data.get('last_name', ''),
                        'rut': user_data.get('rut', ''),
                        'phone': user_data.get('phone', ''),
                        'is_active': user_data.get('is_active', False),
                        'role_name': user_data.get('role', {}).get('name') if isinstance(user_data.get('role'), dict) else 'Sin Rol',
                        'workshop_name': user_data.get('workshop', {}).get('name') if isinstance(user_data.get('workshop'), dict) else 'N/A',
                        'email': None # Columna 'email' no presente en tabla 'employee'
                    }
                    users_list.append(normalized_user)
                
                logger.info(f"✅ Se listaron {len(users_list)} empleados.")
                return users_list, None
            else:
                 logger.warning("⚠️ La consulta a 'employee' no devolvió datos.")
                 return [], None

        except Exception as e:
            error_message = f"Error al listar usuarios y roles: {getattr(e, 'message', str(e))}"
            logger.error(f"❌ {error_message}", exc_info=True)
            return None, error_message

    def get_user_details(self, user_id: str):
        """Obtiene los detalles de un empleado por su UUID."""
        supabase = get_supabase()
        logger.info(f"ℹ️ Obteniendo detalles para empleado ID: {user_id}")

        try:
            response = (
                supabase.table("employee")
                .select(
                     """
                    id, 
                    first_name, 
                    last_name, 
                    rut, 
                    phone, 
                    is_active,
                    role:role_id(name), 
                    workshop:workshop_id(name) 
                    """
                )
                .eq("id", user_id) 
                .maybe_single()    
                .execute()
            )

            logger.debug(f"📊 Respuesta cruda de Supabase (get_user_details): {response.data}")

            if response.data:
                user_data = response.data
                normalized_user = {
                    'id': user_data.get('id'),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'rut': user_data.get('rut', ''),
                    'phone': user_data.get('phone', ''),
                    'is_active': user_data.get('is_active', False),
                    'role_name': user_data.get('role', {}).get('name') if isinstance(user_data.get('role'), dict) else 'Sin Rol',
                    'workshop_name': user_data.get('workshop', {}).get('name') if isinstance(user_data.get('workshop'), dict) else 'N/A',
                    'email': None 
                }
                logger.info(f"✅ Detalles encontrados para {user_id}.")
                return normalized_user, None 
            else:
                logger.warning(f"⚠️ Empleado no encontrado: {user_id}")
                return None, "Empleado no encontrado"

        except Exception as e:
            error_message = f"Error al obtener detalles del usuario {user_id}: {getattr(e, 'message', str(e))}"
            logger.error(f"❌ {error_message}", exc_info=True)
            return None, error_message