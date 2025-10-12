from urllib import request
from ..client.supabase_client import get_supabase

class RolesService:

    @staticmethod
    def get_user_role(user_id: str):
        supabase = get_supabase()
        result = (
            supabase.table("roles_usuario")
            .select("rol")
            .eq("usuario_id", user_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0].get("rol")
        return None

    @staticmethod
    def set_user_role(user_id: str, role: str):
        supabase = get_supabase()
        
        data = {"id": user_id, "rol": role}
        
        result = supabase.table("roles_usuario").upsert(data).execute()
        return bool(result.data)
