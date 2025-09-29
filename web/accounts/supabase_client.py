import os
from supabase import create_client, Client

_supabase: Client | None = None

# Devuelve un cliente Supabase base con ANON_KEY
def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("No se encontraron SUPABASE_URL o SUPABASE_ANON_KEY en el entorno.")
        _supabase = create_client(url, key)
    return _supabase

def get_supabase_with_user(token: str, refresh_token: str) -> Client:
    client = get_supabase()
    client.auth.set_session(token, refresh_token)
    
    return client