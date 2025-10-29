import os
import logging
from supabase import create_client, Client

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)

# Variable global para almacenar la instancia del cliente Supabase (patrón Singleton).
# Esto evita crear una nueva conexión en cada petición.
_supabase: Client | None = None

def get_supabase() -> Client:
    """
    Obtiene una instancia singleton del cliente Supabase con la clave anónima.

    Esta función asegura que solo se cree una instancia del cliente Supabase
    durante el ciclo de vida de la aplicación, mejorando la eficiencia.
    Utiliza las variables de entorno SUPABASE_URL y SUPABASE_ANON_KEY.

    Raises:
        RuntimeError: Si las variables de entorno necesarias no están configuradas.

    Returns:
        Client: La instancia del cliente Supabase.
    """    

    global _supabase
    # Solo crea una nueva instancia si no existe una previamente.
    if _supabase is None:
        logger.info("🔧 (get_supabase) Creando nueva instancia del cliente Supabase...")
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("No se encontraron SUPABASE_URL o SUPABASE_ANON_KEY en el entorno.")
        _supabase = create_client(url, key)
    return _supabase

def get_supabase_with_user(token: str, refresh_token: str) -> Client:
    """
    Obtiene el cliente Supabase y establece la sesión de un usuario autenticado.

    Utiliza la instancia base del cliente y le inyecta el token de acceso y
    el token de refresco del usuario para realizar operaciones autenticadas.

    Args:
        token (str): El token de acceso JWT del usuario.
        refresh_token (str): El token de refresco del usuario.

    Returns:
        Client: El cliente Supabase con la sesión del usuario establecida.
    """

    # Obtiene la instancia singleton del cliente.
    client = get_supabase()
    # Establece la sesión del usuario para que las siguientes peticiones
    # con este cliente se realicen en nombre del usuario.
    client.auth.set_session(token, refresh_token)
    logger.debug("👤 (get_supabase_with_user) Sesión de usuario establecida en el cliente Supabase.")
    return client