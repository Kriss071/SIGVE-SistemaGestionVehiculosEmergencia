import logging
from typing import Any, List, Dict, Optional
from shared.services.base_service import BaseService
from supabase import PostgrestAPIError

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

class EmployeeService(BaseService):
    """
    Servicio para gestionar la lógica de negocio de los Empleados (tabla 'employee').
    Se conecta con Supabase para operaciones CRUD.
    """

    TABLE_NAME = "employee"

    def __init__(self, token: str, refresh_token: str):
        """
        Inicializa el servicio con un cliente Supabase autenticado.
        """
        super().__init__(token, refresh_token)
        logger.debug(f"🔧 Instancia de EmployeeService creada para la tabla '{self.TABLE_NAME}'.")


    def list_employees(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los empleados con sus roles y talleres asociados.
        
        Realiza una consulta a la tabla 'employee' y trae información
        relacionada de las tablas 'role' y 'workshop'.
        
        Returns:
            Una lista de diccionarios, donde cada uno representa un empleado
            con sus datos relacionados aplanados.
        """
        logger.info(f"📄 (list_employees) Obteniendo lista de empleados...")
        try:
            # La consulta pide todos los campos de 'employee' y anida
            # información específica de las tablas relacionadas (rol y taller).
            response = (
                self.client.table(self.TABLE_NAME)
                .select(
                    """
                    *,
                    role:role_id(name),
                    workshop:workshop_id(name)
                    """
                )
                .order("last_name")
                .execute()
            )
            logger.debug(f"📊 (list_employees) Respuesta cruda de Supabase: {response.data}")

            # Proceso de normalización: Aplanar los datos anidados para las plantillas.
            employees = []
            for item in response.data:
                # Extraer y aplanar información del rol
                role_data = item.get('role', {})
                item['role_name'] = role_data.get('name', 'Sin Rol') if isinstance(role_data, dict) else 'Sin Rol'
                
                # Extraer y aplanar información del taller
                workshop_data = item.get('workshop', {})
                item['workshop_name'] = workshop_data.get('name', 'Sin Taller') if isinstance(workshop_data, dict) else 'Sin Taller'
                
                employees.append(item)
            
            logger.info(f"✅ (list_employees) Se procesaron {len(employees)} empleados.")
            return employees
        except Exception as e:
            logger.error(f"❌ (list_employees) Error al obtener empleados: {e}", exc_info=True)
            return []

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un empleado específico por su ID (UUID).
        
        Args:
            employee_id: El UUID del empleado (debe coincidir con auth.users.id).
            
        Returns:
            Un diccionario con los datos del empleado o None si no se encuentra.
        """
        logger.info(f"ℹ️ (get_employee) Obteniendo empleado con ID: {employee_id}")
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .select("*")  # Pedimos todos los campos para el formulario de edición
                .eq("id", employee_id)
                .maybe_single()
                .execute()
            )
            logger.debug(f"📊 (get_employee) Respuesta cruda de Supabase: {response.data}")
            if not response.data:
                logger.warning(f"⚠️ (get_employee) Empleado no encontrado: {employee_id}")
                return None
            
            logger.info(f"✅ (get_employee) Empleado encontrado: {employee_id}")
            return response.data
        except Exception as e:
            logger.error(f"❌ (get_employee) Error al obtener empleado: {e}", exc_info=True)
            return None

    def create_employee(self, data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de empleado.
        
        NOTA: Asume que el 'id' (UUID) proporcionado ya existe en 'auth.users'
        de Supabase.
        
        Args:
            data: Diccionario con los datos del empleado a crear.
            
        Returns:
            True si la creación fue exitosa, False en caso contrario.
        """
        logger.info(f"➕ (create_employee) Intentando crear empleado con ID: {data.get('id')}")
        try:
            response = self.client.table(self.TABLE_NAME).insert(data).execute()
            if not response.data:
                logger.warning(f"⚠️ (create_employee) Supabase no devolvió datos. Creación fallida para ID: {data.get('id')}")
                return False
                
            logger.info(f"✅ (create_employee) Empleado creado exitosamente: {response.data[0].get('id')}")
            return True
        except PostgrestAPIError as e:
            # Error común: 'id' duplicado (ya existe) o 'id' no existe en 'auth.users' (FK)
            logger.error(f"❌ (create_employee) Error de API al crear empleado: {e.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"❌ (create_employee) Error inesperado al crear empleado: {e}", exc_info=True)
            return False

    def create_auth_user(self, email: str, password: str) -> Optional[Any]:
        """Intenta crear un usuario en Supabase Authentication."""
        logger.info(f"🔑 (create_auth_user) Intentando crear usuario en Auth para: {email}")
        try:
            # La función para registrarse se llama 'sign_up'
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
            })
            logger.info(f"✅ (create_auth_user) Usuario de Auth creado exitosamente.")
            return response.user
        except Exception as e:
            logger.error(f"❌ (create_auth_user) Error al crear usuario en Auth: {e}", exc_info=True)
            return None

    def update_employee(self, employee_id: str, data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro de empleado existente.
        
        Args:
            employee_id: El UUID del empleado a actualizar.
            data: Diccionario con los campos a actualizar.
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        logger.info(f"🔄 (update_employee) Intentando actualizar empleado: {employee_id}")
        # Asegurarse de no intentar actualizar la 'id'
        if 'id' in data:
            del data['id']
            
        try:
            response = (
                self.client.table(self.TABLE_NAME)
                .update(data, returning="representation")
                .eq("id", employee_id)
                .execute()
            )
            if not response.data:
                logger.warning(f"⚠️ (update_employee) Supabase no devolvió datos. Actualización fallida para: {employee_id}")
                return False
                
            logger.info(f"✅ (update_employee) Empleado actualizado exitosamente: {employee_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (update_employee) Error inesperado al actualizar empleado: {e}", exc_info=True)
            return False

    def delete_employee(self, employee_id: str) -> bool:
        """
        Elimina un registro de empleado.
        
        NOTA: Esto NO elimina al usuario de Supabase Auth, solo de la tabla 'employee'.
        
        Args:
            employee_id: El UUID del empleado a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        logger.info(f"🗑️ (delete_employee) Intentando eliminar empleado: {employee_id}")
        try:
            response = self.client.table(self.TABLE_NAME).delete().eq("id", employee_id).execute()
            if not response.data:
                logger.warning(f"⚠️ (delete_employee) Supabase no devolvió datos. Eliminación fallida para: {employee_id}")
                return False
                
            logger.info(f"✅ (delete_employee) Empleado eliminado exitosamente: {employee_id}")
            return True
        except Exception as e:
            logger.error(f"❌ (delete_employee) Error inesperado al eliminar empleado: {e}", exc_info=True)
            return False

    # --- Métodos de Catálogo ---

    def get_roles(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de roles para poblar formularios."""
        logger.debug("📚 (get_roles) Obteniendo catálogo de roles...")
        try:
            response = self.client.table("role").select("id, name").order("name").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ (get_roles) Error al obtener roles: {e}", exc_info=True)
            return []

    def get_workshops(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de talleres para poblar formularios."""
        logger.debug("📚 (get_workshops) Obteniendo catálogo de talleres...")
        try:
            response = self.client.table("workshop").select("id, name").order("name").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"❌ (get_workshops) Error al obtener talleres: {e}", exc_info=True)
            return []
