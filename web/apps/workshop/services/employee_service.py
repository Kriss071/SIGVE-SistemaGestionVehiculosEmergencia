import logging
from typing import Dict, List, Any, Optional
from .base_service import WorkshopBaseService

logger = logging.getLogger(__name__)


class EmployeeService(WorkshopBaseService):
    """Servicio para gestionar empleados del taller."""
    
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


