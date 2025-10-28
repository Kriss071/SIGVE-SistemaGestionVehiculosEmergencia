from accounts.client.supabase_client import get_supabase_admin
from supabase import Client
from typing import List, Dict, Any, Tuple, Optional

class UserService:
    
    def __init__(self):
        self.admin_client: Client = get_supabase_admin()

    def list_users_with_roles(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        
        try:
            # --- INICIO DE LA CORRECCIÓN ---
            # 1. Obtenemos la lista de usuarios directamente
            auth_users = self.admin_client.auth.admin.list_users()
            
            # 2. Obtenemos los roles
            roles_resp = self.admin_client.table("roles_usuario").select("*").execute()
            
            # 3. La línea 'auth_users = auth_users_resp.users' se elimina
            roles_data = roles_resp.data
            # --- FIN DE LA CORRECCIÓN ---

            roles_map = {role['usuario_id']: role['rol'] for role in roles_data}
            
            combined_list = []
            for user in auth_users:
                user_id = user.id
                role = roles_map.get(user_id, "user") 
                
                combined_list.append({
                    "id": user_id,
                    "email": user.email,
                    "role": role,
                    "created_at": user.created_at,
                    "last_sign_in_at": user.last_sign_in_at
                })
                
            return combined_list, None
        
        except Exception as e:
            print(f"Error al listar usuarios y roles: {e}")
            return [], str(e)

    def create_user(self, email: str, password: str, role: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        # (Esta función estaba bien, se mantiene igual)
        try:
            user_resp = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True 
            })
            
            if not user_resp or not user_resp.user:
                 raise Exception("No se pudo crear el usuario en Auth.")
            
            user = user_resp.user
            
            role_data = { 
                "usuario_id": user.id, 
                "rol": role 
            }
            self.admin_client.table("roles_usuario").upsert(role_data).execute()
            
            user_dict = {
                "id": user.id,
                "email": user.email,
                "role": role
            }
            return user_dict, None
        
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None, str(e)

    def delete_user(self, user_id: str) -> Tuple[bool, Optional[str]]:
        # (Esta función estaba bien, se mantiene igual)
        try:
            self.admin_client.auth.admin.delete_user(user_id)
            return True, None
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False, str(e)