import logging
from functools import wraps
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from accounts.decorators import _get_authenticated_user
from accounts.client.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def require_workshop_user(view_func):
    """
    Decorador para vistas que requieren que el usuario pertenezca a un taller.
    
    Verifica que:
    - El usuario esté autenticado
    - Tenga un workshop_id no nulo
    - Su rol sea "Admin Taller" o "Mecánico"
    
    Args:
        view_func: La función de vista a decorar.
    
    Returns:
        La función de vista decorada.
    """
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        # Primero verificar autenticación
        user, response_redirect = _get_authenticated_user(request)
        
        if response_redirect:
            return response_redirect
        
        user_id = getattr(user, 'id', None)
        if not user_id:
            logger.error("❌ (require_workshop_user) Usuario sin ID.")
            return redirect('unauthorized')
        
        try:
            supabase = get_supabase()
            
            # Obtener el perfil del usuario con su rol y taller
            profile_resp = (
                supabase.table("user_profile")
                .select("id, workshop_id, role:role_id(name)")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            
            if not profile_resp.data:
                logger.warning(f"⚠️ (require_workshop_user) Perfil no encontrado para usuario {user_id}")
                messages.error(request, "No se encontró el perfil de usuario.")
                return redirect('unauthorized')
            
            profile = profile_resp.data
            workshop_id = profile.get('workshop_id')
            role_data = profile.get('role', {})
            role_name = role_data.get('name', '') if isinstance(role_data, dict) else ''
            
            # Verificar que tenga un taller asignado
            if not workshop_id:
                logger.warning(f"⚠️ (require_workshop_user) Usuario {user_id} no tiene taller asignado")
                messages.error(request, "No tienes un taller asignado. Contacta al administrador.")
                return redirect('unauthorized')
            
            # Verificar que sea Admin Taller o Mecánico (o Super Admin)
            allowed_roles = ['Admin Taller', 'Mecánico', 'Super Admin']
            if role_name not in allowed_roles:
                logger.warning(f"⚠️ (require_workshop_user) Usuario {user_id} con rol '{role_name}' intentó acceder")
                messages.error(request, f"Acceso denegado. Se requiere rol de taller (Admin Taller o Mecánico).")
                return redirect('unauthorized')
            
            # Almacenar información en la sesión para uso futuro
            request.session['sb_user_id'] = user_id
            request.session['sb_user_role'] = role_name
            request.session['sb_workshop_id'] = workshop_id
            
            # Agregar al request para acceso directo en la vista
            request.workshop_id = workshop_id
            request.user_role = role_name
            
            logger.info(f"✅ (require_workshop_user) Acceso concedido a {user_id} (Rol: {role_name}, Taller: {workshop_id})")
            
        except Exception as e:
            logger.error(f"❌ (require_workshop_user) Error verificando permisos: {e}", exc_info=True)
            messages.error(request, "Error al verificar permisos.")
            return redirect('unauthorized')
        
        # Ejecutar la vista original
        return view_func(request, *args, **kwargs)
    
    return _wrapped


def require_admin_taller(view_func):
    """
    Decorador para vistas que requieren específicamente el rol "Admin Taller".
    
    Debe usarse junto con @require_workshop_user o después de él.
    
    Args:
        view_func: La función de vista a decorar.
    
    Returns:
        La función de vista decorada.
    """
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        # Primero verificar autenticación y pertenencia al taller
        user, response_redirect = _get_authenticated_user(request)
        
        if response_redirect:
            return response_redirect
        
        user_id = getattr(user, 'id', None)
        if not user_id:
            return redirect('unauthorized')
        
        try:
            supabase = get_supabase()
            
            # Obtener el rol del usuario
            profile_resp = (
                supabase.table("user_profile")
                .select("role:role_id(name), workshop_id")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            
            if not profile_resp.data:
                logger.warning(f"⚠️ (require_admin_taller) Perfil no encontrado para {user_id}")
                messages.error(request, "No se encontró el perfil de usuario.")
                return redirect('unauthorized')
            
            profile = profile_resp.data
            role_data = profile.get('role', {})
            role_name = role_data.get('name', '') if isinstance(role_data, dict) else ''
            
            # Verificar que sea Admin Taller (o Super Admin)
            if role_name not in ['Admin Taller', 'Super Admin']:
                logger.warning(f"⚠️ (require_admin_taller) Usuario {user_id} con rol '{role_name}' intentó acceder a función de Admin")
                messages.error(request, "Acceso denegado. Solo el Administrador del Taller puede realizar esta acción.")
                return redirect('workshop:dashboard')
            
            logger.info(f"✅ (require_admin_taller) Acceso admin concedido a {user_id}")
            
        except Exception as e:
            logger.error(f"❌ (require_admin_taller) Error: {e}", exc_info=True)
            messages.error(request, "Error al verificar permisos.")
            return redirect('unauthorized')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped


