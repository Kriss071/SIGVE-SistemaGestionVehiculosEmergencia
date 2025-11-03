import logging
from functools import wraps
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from accounts.client.supabase_client import get_supabase
from accounts.services.roles_services import RolesService


logger = logging.getLogger(__name__) 

# --- Función Auxiliar ---

def _get_authenticated_user(request: HttpRequest) -> tuple[object | None, HttpResponseRedirect | None]:
    """
    Función auxiliar para verificar el token de Supabase y obtener el usuario autenticado.

    Busca el token en la sesión, lo valida contra Supabase y devuelve el objeto User
    o una redirección a 'login' si falla la autenticación.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        Una tupla: (User object | None, RedirectResponse | None).
        - Si la autenticación es exitosa: (User, None)
        - Si falla la autenticación: (None, RedirectResponse)
    """

    token = request.session.get('sb_access_token')

    # 1. Verificar si hay token en la sesión
    if not token:
        logger.warning("🚫 (_get_authenticated_user) No hay token de Supabase en la sesión.")
        return None, redirect('login')

    supabase = get_supabase()
    try:
        # 2. Validar el token y obtener el usuario de Supabase
        logger.debug("🔒 (_get_authenticated_user) Validando token y obteniendo usuario...")
        user_resp = supabase.auth.get_user(token)
        user = getattr(user_resp, "user", None)
        
        # 3. Verificar si el usuario es válido
        if not user:
            logger.warning("🚫 (_get_authenticated_user) Token inválido o usuario no encontrado. Limpiando sesión.")
            request.session.flush()
            return None, redirect('login')
            
        logger.debug(f"👤 (_get_authenticated_user) Usuario {user.id} autenticado.")
        return user, None # Autenticación exitosa

    except Exception as e:
        # Capturar cualquier error durante la validación
        logger.error(f"❌ (_get_authenticated_user) Error durante validación de token: {e}", exc_info=True)
        request.session.flush() # Limpiar sesión en caso de error
        return None, redirect('login')


# --- Decoradores ---

def require_supabase_login(view_func):
    """
    Decorador para vistas de Django que requieren un usuario autenticado vía Supabase.

    Utiliza _get_authenticated_user para verificar la autenticación. Si es exitosa,
    obtiene el rol del usuario (usando RolesService) y lo almacena en la sesión 
    (`sb_user_id`, `sb_user_role`) antes de ejecutar la vista.

    Args:
        view_func: La función de vista original a decorar.

    Returns:
        La función de vista decorada.
    """
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        # Llama a la función auxiliar para manejar la autenticación
        user, response_redirect = _get_authenticated_user(request)

        # Redirige si la autenticación falló
        if response_redirect:
            return response_redirect 


        # Si user no es None (autenticación exitosa), proceder
        if user:
            try:
                # Obtener el rol del usuario usando RolesService
                role = RolesService.get_user_role(user.id)
                logger.info(f"🎭 (require_login) Rol obtenido para {user.id}: {role}")
                
                # Almacenar ID y Rol en la sesión de Django
                request.session["sb_user_id"] = user.id
                request.session["sb_user_role"] = role or "Usuario" 
                logger.debug(f"ℹ️ (require_login) Sesión actualizada: ID={user.id}, Rol={request.session['sb_user_role']}")
            
            except Exception as e:
                 # Capturar error al obtener el rol
                logger.error(f"❌ (require_login) Error al obtener rol para {user.id}: {e}", exc_info=True)
                messages.error(request, "Error al verificar los permisos del usuario.")
                request.session.flush() # Limpiar sesión si falla la obtención del rol
                return redirect('login')
        else:
            # Esto no debería ocurrir si _get_authenticated_user funciona correctamente,
            # pero es una salvaguarda.
            logger.error("❌ (require_login) _get_authenticated_user devolvió (None, None), estado inesperado.")
            return redirect('login')


        # Ejecutar la vista original si todo está bien
        return view_func(request, *args, **kwargs)
    return _wrapped


def require_role(required_role):
    """
    Decorador de fábrica para vistas de Django que requieren un rol específico.

    Utiliza _get_authenticated_user para la autenticación inicial. Si es exitosa,
    consulta la tabla `user_profile` (uniéndola con `role`) para obtener el nombre 
    del rol actual del usuario y lo compara con `required_role`.

    Args:
        required_role (str): El nombre exacto del rol requerido (sensible a mayúsculas/minúsculas). 
                             Ej: "Admin SIGVE", "Admin Taller", "Mecánico".

    Returns:
        Una función decoradora que toma la función de vista como argumento.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs):
            # Llama a la función auxiliar para manejar la autenticación
            user, response_redirect = _get_authenticated_user(request)
            
            if response_redirect:
                return response_redirect # Redirige si la autenticación falló
            
            # Si user no es None (autenticación exitosa), proceder a verificar el rol
            user_id = getattr(user, 'id', None) 
            if user_id:
                try:
                    logger.debug(f"👤 (require_role) Verificando si {user_id} tiene el rol '{required_role}'...")
                    supabase = get_supabase() # Re-obtener cliente por si acaso
                    
                    # Buscar el rol del usuario desde la tabla 'user_profile' uniéndola con 'role'
                    role_resp = (
                        supabase.table("user_profile")
                        .select("role_id, role:role_id(name)") 
                        .eq("id", user_id)                   
                        .maybe_single()                      
                        .execute()
                    )
                    
                    user_role_name = '' 
                    
                    # Verificar si se encontró el perfil de usuario y extraer el nombre del rol
                    if not role_resp.data:
                        logger.warning(f"⚠️ (require_role) Usuario {user_id} no encontrado en 'user_profile'. Acceso denegado.")
                        messages.error(request, "No tienes permisos (perfil de usuario no encontrado).")
                        return redirect('login') 
                    
                    role_relation_data = role_resp.data.get('role')
                    if isinstance(role_relation_data, dict):
                        user_role_name = role_relation_data.get('name', '')
                        logger.debug(f"🎭 (require_role) Rol obtenido de relación: '{user_role_name}'")
                    else:
                        role_id = role_resp.data.get('role_id')
                        if role_id:
                            logger.debug(f"🤔 (require_role) Buscando nombre para role_id={role_id}...")
                            role_direct_result = (
                                supabase.table("role")
                                .select("name")
                                .eq("id", role_id)
                                .maybe_single()
                                .execute()
                            )
                            if role_direct_result.data:
                                user_role_name = role_direct_result.data.get('name', '')
                                logger.debug(f"🎭 (require_role) Rol obtenido directo: '{user_role_name}'")
                            else:
                                 logger.warning(f"⚠️ (require_role) No se encontró nombre para role_id={role_id}.")
                        else:
                            logger.warning(f"⚠️ (require_role) Usuario {user_id} sin 'role_id'.")
                            
                    # Comparar el rol obtenido con el requerido
                    if user_role_name != required_role:
                        logger.warning(f"🚫 (require_role) Acceso denegado: '{user_role_name}' != '{required_role}'.")
                        messages.error(request, f"Acceso denegado. Se requiere el rol: '{required_role}'")
                        return redirect('login') 
                    
                    logger.info(f"✅ (require_role) Acceso concedido para {user_id} (Rol: '{user_role_name}')")
                    
                except Exception as e:
                    logger.error(f"❌ (require_role) Error verificando rol para {user_id} (req: '{required_role}'): {e}", exc_info=True)
                    messages.error(request, "Error al verificar permisos.")
                    # Considerar si limpiar sesión aquí es apropiado o solo redirigir
                    # request.session.flush() 
                    return redirect('login')
            else:
                # Salvaguarda, aunque no debería ocurrir
                logger.error("❌ (require_role) _get_authenticated_user devolvió un objeto sin 'id' o None.")
                return redirect('login')

            # Ejecutar la vista original si el rol coincide
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator