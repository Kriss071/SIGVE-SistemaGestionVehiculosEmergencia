import logging
from typing import Dict, List, Any, Optional
from .base_service import WorkshopBaseService
from accounts.client.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


class EmployeeService(WorkshopBaseService):
    """Servicio para gestionar empleados del taller."""
    
    @staticmethod
    def create_employee(
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role_id: int,
        workshop_id: int,
        rut: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo empleado del taller (Admin Taller o Mecánico).
        
        Args:
            email: Correo electrónico del empleado
            password: Contraseña del empleado
            first_name: Nombre del empleado
            last_name: Apellido del empleado
            role_id: ID del rol (Admin Taller o Mecánico)
            workshop_id: ID del taller
            rut: RUT del empleado (opcional)
            phone: Teléfono del empleado (opcional)
            
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
            error_msg = str(auth_error)
            if "already registered" in error_msg.lower() or "duplicate" in error_msg.lower():
                return {"success": False, "user_id": None, "error": "El correo electrónico ya está registrado."}
            return {"success": False, "user_id": None, "error": "Error creando el usuario."}
        
        # Paso 2: Crear perfil en user_profile
        try:
            client = WorkshopBaseService.get_client()
            profile_data = {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "rut": rut,
                "phone": phone,
                "role_id": role_id,
                "workshop_id": workshop_id,
                "is_active": True
            }
            
            result = client.table("user_profile") \
                .insert(profile_data) \
                .execute()
            
            if not result.data:
                raise Exception("No se pudo crear el perfil del usuario.")
            
            logger.info(f"✅ Empleado {email} creado correctamente con ID {user_id}")
            return {"success": True, "user_id": user_id, "error": None}
            
        except Exception as profile_error:
            logger.error(f"❌ Error creando perfil del usuario: {profile_error}", exc_info=True)
            
            # Revertir: eliminar usuario de auth
            try:
                admin_client.auth.admin.delete_user(user_id)
                logger.info(f"♻️ Usuario {user_id} eliminado de auth tras error en perfil.")
            except Exception as cleanup_error:
                logger.error(f"⚠️ Error al revertir usuario en auth: {cleanup_error}", exc_info=True)
            
            return {"success": False, "user_id": user_id, "error": "Error creando el perfil del empleado."}
    
    @staticmethod
    def get_all_employees(workshop_id: int):
        """
        Obtiene todos los empleados de un taller.
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Lista de empleados con información de rol.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("user_profile") \
            .select("""
                id,
                first_name,
                last_name,
                rut,
                phone,
                is_active,
                created_at,
                role:role_id(id, name)
            """) \
            .eq("workshop_id", workshop_id) \
            .order("first_name")
        
        return WorkshopBaseService._execute_query(query, "get_all_employees")
    
    @staticmethod
    def get_employee(user_id: str, workshop_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un empleado específico del taller.
        
        Args:
            user_id: ID del usuario.
            workshop_id: ID del taller.
            
        Returns:
            Datos del empleado o None.
        """
        client = WorkshopBaseService.get_client()
        
        query = client.table("user_profile") \
            .select("""
                *,
                role:role_id(*)
            """) \
            .eq("id", user_id) \
            .eq("workshop_id", workshop_id)
        
        return WorkshopBaseService._execute_single(query, "get_employee")
    
    @staticmethod
    def get_mechanics(workshop_id: int):
        """
        Obtiene solo los mecánicos del taller (para asignar a órdenes).
        
        Args:
            workshop_id: ID del taller.
            
        Returns:
            Lista de mecánicos activos.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            # Obtener el ID del rol "Mecánico"
            mechanic_role = client.table("role") \
                .select("id") \
                .eq("name", "Mecánico") \
                .maybe_single() \
                .execute()
            
            if not mechanic_role.data:
                logger.warning("⚠️ No se encontró el rol 'Mecánico'")
                return []
            
            mechanic_role_id = mechanic_role.data['id']
            
            # Obtener mecánicos del taller
            query = client.table("user_profile") \
                .select("id, first_name, last_name, rut") \
                .eq("workshop_id", workshop_id) \
                .eq("role_id", mechanic_role_id) \
                .eq("is_active", True) \
                .order("first_name")
            
            return WorkshopBaseService._execute_query(query, "get_mechanics")
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo mecánicos: {e}", exc_info=True)
            return []
    
    @staticmethod
    def update_employee(user_id: str, workshop_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un empleado del taller.
        
        Args:
            user_id: ID del usuario.
            workshop_id: ID del taller.
            data: Datos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        client = WorkshopBaseService.get_client()
        
        try:
            result = client.table("user_profile") \
                .update(data) \
                .eq("id", user_id) \
                .eq("workshop_id", workshop_id) \
                .execute()
            
            logger.info(f"✅ Empleado {user_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando empleado {user_id}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def deactivate_employee(user_id: str, workshop_id: int) -> bool:
        """
        Desactiva un empleado del taller.
        
        Args:
            user_id: ID del usuario.
            workshop_id: ID del taller.
            
        Returns:
            True si se desactivó correctamente, False en caso contrario.
        """
        return EmployeeService.update_employee(user_id, workshop_id, {'is_active': False})
    
    @staticmethod
    def activate_employee(user_id: str, workshop_id: int) -> bool:
        """
        Activa un empleado del taller.
        
        Args:
            user_id: ID del usuario.
            workshop_id: ID del taller.
            
        Returns:
            True si se activó correctamente, False en caso contrario.
        """
        return EmployeeService.update_employee(user_id, workshop_id, {'is_active': True})
    
    @staticmethod
    def get_available_roles():
        """
        Obtiene los roles disponibles para asignar a empleados del taller.
        
        Returns:
            Lista de roles (Admin Taller y Mecánico).
        """
        client = WorkshopBaseService.get_client()
        
        # Solo devolver roles relevantes para talleres
        query = client.table("role") \
            .select("id, name, description") \
            .in_("name", ["Admin Taller", "Mecánico"]) \
            .order("name")
        
        return WorkshopBaseService._execute_query(query, "get_available_roles")


