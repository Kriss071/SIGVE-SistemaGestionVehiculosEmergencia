import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from .client.supabase_client import get_supabase
from .decorators import require_supabase_login
from .services.auth_service import AuthService
from .services.roles_services import RolesService

logger = logging.getLogger(__name__)


def get_redirect_url_by_role(role: str) -> str:
    """
    Determina la URL de redirección basada en el rol del usuario.
    
    Args:
        role (str): El rol del usuario.
        
    Returns:
        str: El nombre de la URL a la que se debe redirigir.
    """
    # Mapeo de roles a URLs de redirección
    role_redirects = {
        'Super Admin': 'sigve:dashboard',  # Super Admin va al panel SIGVE por defecto
        'Admin SIGVE': 'sigve:dashboard',  # Admin SIGVE va a su panel
        'Admin Taller': 'vehicle_list',
        # 'Mecánico': 'workshop:maintenance',
        # 'Jefe Cuartel': 'fire_station:dashboard',
    }
    
    # Obtener la URL de redirección según el rol, o usar 'vehicle_list' por defecto
    redirect_url = role_redirects.get(role, 'vehicle_list')
    logger.info(f"🔀 Rol '{role}' será redirigido a '{redirect_url}'")
    
    return redirect_url 

def login_view(request):
    """
    Gestiona el proceso de inicio de sesión del usuario.

    - Si el usuario ya está autenticado (tiene token en sesión), redirige según su rol.
    - Si es método GET, muestra el formulario de login.
    - Si es método POST:
        - Valida el formulario.
        - Llama a AuthService.login para autenticar con Supabase.
        - Si la autenticación es exitosa:
            - Limpia la sesión anterior.
            - Guarda los tokens, email, ID y rol del usuario en la sesión de Django.
            - Establece la sesión para que expire al cerrar el navegador.
            - Muestra un mensaje de éxito y redirige según el rol del usuario.
        - Si la autenticación falla (credenciales incorrectas), muestra el formulario con errores.
        - Si el formulario es inválido, muestra errores de validación.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponse: Renderiza el template de login con errores o redirige según el rol.
    """

    # 1. Redirigir si ya está logueado
    if request.session.get("sb_access_token"):
        user_role = request.session.get("sb_user_role", "Usuario")
        redirect_url = get_redirect_url_by_role(user_role)
        logger.debug(f"👤 (login_view) Usuario ya autenticado con rol '{user_role}', redirigiendo a '{redirect_url}'.")
        return redirect(redirect_url)

    # 2. Procesar el envío del formulario (POST)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            logger.debug("✅ (login_view) Formulario de login válido. Intentando autenticar...")
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # 2a. Llamar al servicio de autenticación
            session, error = AuthService.login(email, password)
            
            # 2b. Manejar fallo de autenticación
            if error or not session:
                logger.warning(f"🚫 (login_view) Fallo de autenticación para {email}: {error}")
                messages.error(request, error or "Credenciales inválidas. Por favor, verifica tu email y contraseña.")
                return render(request, "accounts/login.html", {"form": form})

            # 2c. Autenticación exitosa: Configurar sesión de Django
            logger.info(f"🔑 (login_view) Autenticación exitosa para {email}.")
            request.session.flush() # Limpiar cualquier sesión anterior
            request.session["sb_access_token"] = session.access_token
            request.session["sb_refresh_token"] = session.refresh_token
            request.session["sb_user_email"] = form.cleaned_data["email"]
            request.session.set_expiry(0) # La sesión expira al cerrar el navegador

            # 2d. Obtener y guardar ID y Rol del usuario en la sesión
            user_id = session.user.id
            try:
                user_role = RolesService.get_user_role(user_id)
                logger.info(f"🎭 (login_view) Rol obtenido para {user_id}: {user_role}")
                request.session["sb_user_id"] = user_id
                # Usar "Usuario" como default si no se encuentra rol específico
                request.session["sb_user_role"] = user_role or "Usuario"
            except Exception as e:
                logger.error(f"❌ (login_view) Error obteniendo rol para {user_id} tras login: {e}", exc_info=True)
                messages.error(request, "Inicio de sesión exitoso, pero hubo un problema al cargar tus permisos.")
                # Aunque hubo error con el rol, el login fue exitoso, continuar pero sin rol específico
                request.session["sb_user_id"] = user_id
                request.session["sb_user_role"] = "Usuario" # Rol genérico en caso de error

            logger.debug(f"ℹ️ (login_view) Sesión configurada: ID={user_id}, Rol={request.session['sb_user_role']}")
            
            # 2e. Determinar URL de redirección según el rol
            redirect_url = get_redirect_url_by_role(request.session['sb_user_role'])
            messages.success(request, f"¡Bienvenido! Has iniciado sesión como {request.session['sb_user_role']}")
            
            return redirect(redirect_url)
        else:
            # 2e. Formulario inválido
            logger.warning("⚠️ (login_view) Formulario de login inválido.")
            messages.error(request, "Credenciales inválidas. Por favor, verifica tu email y contraseña.")

    # 3. Mostrar el formulario vacío (GET o POST inválido)
    else:
        form = LoginForm()
        logger.debug("📄 (login_view) Mostrando formulario de login (GET).")

    # Renderizar la plantilla de login con el formulario (vacío o con errores)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Gestiona el cierre de sesión del usuario.

    Llama a AuthService.logout() para invalidar la sesión en Supabase (si aplica),
    limpia la sesión de Django, muestra un mensaje informativo y redirige
    a la vista de login.

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponseRedirect: Redirige siempre a la vista 'login'.
    """
    user_email = request.session.get("sb_user_email", "Usuario desconocido")
    logger.info(f"🚪 (logout_view) Cerrando sesión para {user_email}...")

    # 1. Intentar cerrar sesión en Supabase (AuthService maneja errores internos)
    AuthService.logout()
    # 2. Limpiar la sesión de Django
    request.session.flush()
    # 3. Mostrar mensaje y redirigir
    messages.info(request, "Sesión cerrada.")
    return redirect("login")


def unauthorized_view(request):
    """
    Muestra una página indicando que el usuario no tiene permisos.

    Renderiza el template 'accounts/unauthorized.html' con un estado HTTP 403 (Forbidden).

    Args:
        request: El objeto HttpRequest de Django.

    Returns:
        HttpResponse: La página de "no autorizado" renderizada.
    """
    logger.warning(f"🚫 (unauthorized_view) Acceso no autorizado solicitado por usuario {request.session.get('sb_user_id', 'desconocido')}.")
    return render(request, "accounts/unauthorized.html", status=403)
