import logging
from functools import wraps
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from accounts.decorators import _get_authenticated_user
from accounts.client.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def require_fire_station_user(view_func):
    """
    Decorador para vistas que requieren que el usuario pertenezca a un cuartel.
    
    Verifica que:
    - El usuario esté autenticado
    - Tenga un fire_station_id no nulo
    - Su rol sea apropiado para cuartel
    
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
            logger.error("❌ (require_fire_station_user) Usuario sin ID.")
            return redirect('unauthorized')
        
        try:
            supabase = get_supabase()
            
            # Obtener el perfil del usuario con su rol y cuartel
            profile_resp = (
                supabase.table("user_profile")
                .select("id, fire_station_id, role:role_id(name), fire_station:fire_station_id(id, name)")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            
            if not profile_resp.data:
                logger.warning(f"⚠️ (require_fire_station_user) Perfil no encontrado para usuario {user_id}")
                messages.error(request, "No se encontró el perfil de usuario.")
                return redirect('unauthorized')
            
            profile = profile_resp.data
            fire_station_id = profile.get('fire_station_id')
            role_data = profile.get('role', {})
            role_name = role_data.get('name', '') if isinstance(role_data, dict) else ''
            
            # Obtener información del cuartel
            fire_station_data = profile.get('fire_station', {})
            fire_station_name = fire_station_data.get('name', '') if isinstance(fire_station_data, dict) else ''
            
            # Verificar que tenga un cuartel asignado
            if not fire_station_id:
                logger.warning(f"⚠️ (require_fire_station_user) Usuario {user_id} no tiene cuartel asignado")
                messages.error(request, "No tienes un cuartel asignado. Contacta al administrador.")
                return redirect('unauthorized')
            
            # Almacenar información en la sesión para uso futuro
            request.session['sb_user_id'] = user_id
            request.session['sb_user_role'] = role_name
            request.session['role_name'] = role_name
            request.session['fire_station_id'] = fire_station_id
            request.session['fire_station_name'] = fire_station_name
            
            # Agregar al request para acceso directo en la vista
            request.fire_station_id = fire_station_id
            request.user_role = role_name
            
            logger.info(f"✅ (require_fire_station_user) Acceso concedido a {user_id} (Rol: {role_name}, Cuartel: {fire_station_id})")
            
        except Exception as e:
            logger.error(f"❌ (require_fire_station_user) Error verificando permisos: {e}", exc_info=True)
            messages.error(request, "Error al verificar permisos.")
            return redirect('unauthorized')
        
        # Ejecutar la vista original
        return view_func(request, *args, **kwargs)
    
    return _wrapped


def require_jefe_cuartel(view_func):
    """
    Decorador para vistas que requieren específicamente el rol "Jefe Cuartel".
    
    Debe usarse junto con @require_fire_station_user o después de él.
    
    Args:
        view_func: La función de vista a decorar.
    
    Returns:
        La función de vista decorada.
    """
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        # Primero verificar autenticación y pertenencia al cuartel
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
                .select("role:role_id(name), fire_station_id")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            
            if not profile_resp.data:
                logger.warning(f"⚠️ (require_jefe_cuartel) Perfil no encontrado para {user_id}")
                messages.error(request, "No se encontró el perfil de usuario.")
                return redirect('unauthorized')
            
            profile = profile_resp.data
            role_data = profile.get('role', {})
            role_name = role_data.get('name', '') if isinstance(role_data, dict) else ''
            
            # Verificar que sea Jefe Cuartel (o Super Admin)
            if role_name not in ['Jefe Cuartel', 'Super Admin']:
                logger.warning(f"⚠️ (require_jefe_cuartel) Usuario {user_id} con rol '{role_name}' intentó acceder a función de Jefe")
                messages.error(request, "Acceso denegado. Solo el Jefe de Cuartel puede realizar esta acción.")
                return redirect('fire_station:dashboard')
            
            logger.info(f"✅ (require_jefe_cuartel) Acceso jefe concedido a {user_id}")
            
        except Exception as e:
            logger.error(f"❌ (require_jefe_cuartel) Error: {e}", exc_info=True)
            messages.error(request, "Error al verificar permisos.")
            return redirect('unauthorized')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped

