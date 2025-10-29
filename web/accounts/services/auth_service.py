import logging
from ..client.supabase_client import get_supabase
from supabase import AuthApiError

# Inicializa el logger para este módulo.
logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio para gestionar la autenticación de usuarios con Supabase.

    Encapsula la lógica para iniciar y cerrar sesión, manejando la comunicación
    con el cliente de Supabase y la gestión de posibles errores.
    """
    @staticmethod
    def login(email: str, password: str):
        """
        Autentica a un usuario utilizando email y contraseña.

        Args:
            email (str): Correo electrónico del usuario.
            password (str): Contraseña del usuario.

        Returns:
            tuple: Una tupla conteniendo la sesión del usuario si fue exitosa (o None)
                   y un mensaje de error si ocurrió alguno (o None).
        """
        
        logger.info(f"🔑 (login) Intentando iniciar sesión para el usuario: {email}")
        supabase = get_supabase()
        
        try:           
            # Llama a la API de Supabase para iniciar sesión con email y contraseña.
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            # Validar que la respuesta contiene una sesión y un token de acceso
            if not getattr(res, "session", None) or not getattr(res.session, "access_token", None):
                logger.warning(f"🚫 (login) Credenciales inválidas para el usuario: {email}")
                return None, "Credenciales inválidas."
            
            logger.info(f"✅ (login) Inicio de sesión exitoso para: {email}")
            return res.session, None
        except AuthApiError as e:
            # Captura errores específicos de la API de autenticación para dar feedback más claro.
            logger.error(f"❌ (login) Error de AuthApiError para {email}: {e}", exc_info=True)
            return None, f"Error al iniciar sesión: {str(e)}"

        except Exception as e:
            # Captura cualquier otro error inesperado durante el proceso.
            logger.error(f"❌ (login) Error inesperado para {email}: {e}", exc_info=True)
            return None, "Ocurrió un error inesperado."
        
    @staticmethod
    def logout():
        """
        Cierra la sesión del usuario actual en Supabase.

        Returns:
            str | None: Un mensaje de error si la operación falla, de lo contrario None.
        """

        logger.info("🚪 (logout) Intentando cerrar sesión en Supabase.")
        try:
            # Llama al método de Supabase para invalidar la sesión actual.
            get_supabase().auth.sign_out()
            logger.info("✅ (logout) Sesión cerrada exitosamente en Supabase.")
            return None
        except Exception as e:
            logger.error(f"❌ (logout) Error al cerrar sesión en Supabase: {e}", exc_info=True)
            return f"Error al cerrar sesión en Supabase: {e}"