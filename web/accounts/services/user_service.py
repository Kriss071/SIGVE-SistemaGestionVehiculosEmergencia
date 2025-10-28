# En: web/administracion/services/user_service.py
from accounts.client.supabase_client import get_supabase_admin
from supabase import Client
from typing import List, Dict, Any, Tuple, Optional
from postgrest.exceptions import APIError # Importar para manejo de errores

class UserService:

    def __init__(self):
        self.admin_client: Client = get_supabase_admin()

    def list_users_with_roles(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Obtiene usuarios de Auth, busca su info y rol en 'employee',
        y finalmente busca el nombre del rol en 'role'.
        """
        try:
            # 1. Obtener usuarios de Auth
            auth_users = self.admin_client.auth.admin.list_users()

            # 2. Obtener todos los registros de 'employee' (incluyendo role_id)
            employees_resp = self.admin_client.table("employee").select("id, role_id").execute()
            employee_data = employees_resp.data
            # Crear un mapa: user_id -> role_id
            employee_role_map = {emp['id']: emp['role_id'] for emp in employee_data if 'id' in emp and 'role_id' in emp}

            # 3. Obtener todos los roles de la tabla 'role' (id y name)
            roles_resp = self.admin_client.table("role").select("id, name").execute()
            roles_data = roles_resp.data
            # Crear un mapa: role_id -> role_name
            role_id_name_map = {role['id']: role['name'] for role in roles_data if 'id' in role and 'name' in role}

            # 4. Combinar la información
            combined_list = []
            for user in auth_users:
                user_id = user.id
                
                # Buscar el role_id en el mapa de empleados
                role_id = employee_role_map.get(user_id)
                
                # Buscar el nombre del rol usando role_id, o usar "user" por defecto si no hay empleado o rol
                role_name = role_id_name_map.get(role_id, "Sin Asignar") if role_id is not None else "Sin Registro Employee"

                combined_list.append({
                    "id": user_id,
                    "email": user.email,
                    "role": role_name, # Nombre del rol obtenido
                    "created_at": user.created_at,
                    "last_sign_in_at": user.last_sign_in_at
                    # Podrías añadir first_name, last_name aquí si los seleccionas de 'employee'
                })

            return combined_list, None

        except APIError as e:
            print(f"APIError al listar usuarios y roles: {e.message} (Code: {e.code})")
            return [], str(e)
        except Exception as e:
            print(f"Error inesperado al listar usuarios y roles: {e}")
            return [], str(e)

    def create_user(self, email: str, password: str, role_name: str, first_name: str, last_name: str, is_active: bool = True) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Crea un usuario en Auth y LUEGO crea su registro correspondiente en 'employee' con el rol.
        Requiere first_name y last_name explícitamente.
        """
        try:
            # Paso 1: Encontrar el ID del rol basado en su nombre
            role_resp = (
                self.admin_client.table("role")
                .select("id")
                .eq("name", role_name)
                .maybe_single()
                .execute()
            )
            if not role_resp.data or "id" not in role_resp.data:
                raise Exception(f"No se encontró un rol con el nombre '{role_name}'.")
            target_role_id = role_resp.data["id"]

            # Paso 2: Crear el usuario en Auth
            user_resp = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            if not user_resp or not user_resp.user:
                 raise Exception("No se pudo crear el usuario en Auth.")
            user = user_resp.user

            # Paso 3: Crear la entrada en la tabla 'employee'
            employee_data = {
                "id": user.id,
                "role_id": target_role_id,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": is_active
                # Añade otros campos si son necesarios y los recibes como parámetro
            }
            # Usamos INSERT aquí porque es un usuario nuevo, no debería existir en 'employee'
            insert_resp = self.admin_client.table("employee").insert(employee_data).execute()
            # Podrías añadir manejo de errores si la inserción falla

            user_dict = {
                "id": user.id,
                "email": user.email,
                "role": role_name # Devolvemos el nombre del rol
            }
            return user_dict, None

        except APIError as e:
            print(f"APIError al crear usuario o asignar rol: {e.message} (Code: {e.code})")
            # Podrías intentar borrar el usuario de Auth si falló la inserción en employee
            return None, str(e.message)
        except Exception as e:
            print(f"Error inesperado al crear usuario: {e}")
            # Podrías intentar borrar el usuario de Auth si falló la inserción en employee
            return None, str(e)

    def delete_user(self, user_id: str) -> Tuple[bool, Optional[str]]:
  
        try:
           
            self.admin_client.auth.admin.delete_user(user_id)
            return True, None
        except APIError as e:
             print(f"APIError al eliminar usuario {user_id}: {e.message} (Code: {e.code})")
             return False, str(e.message)
        except Exception as e:
            print(f"Error inesperado al eliminar usuario {user_id}: {e}")
            return False, str(e)