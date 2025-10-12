from ..client.supabase_client import get_supabase
from supabase import AuthApiError

class AuthService:
    
    @staticmethod
    def login(email: str, password: str):
        supabase = get_supabase()
        
        try:           
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if not getattr(res, "session", None) or not getattr(res.session, "access_token", None):
                return None, "Credenciales inválidas."
            
            return res.session, None
        except AuthApiError as e:
            return None, f"Error al iniciar sesión: {str(e)}"
        
    @staticmethod
    def logout():
        try:
            get_supabase().auth.sign_out()
            return None
        except Exception as e:
            return f"Error al cerrar sesión en Supabase: {e}"