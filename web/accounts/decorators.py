from functools import wraps
from django.http import HttpRequest
from django.shortcuts import redirect
from accounts.client.supabase_client import get_supabase
from accounts.services.roles_services import RolesService

def require_supabase_login(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        token = request.session.get('sb_access_token')
        if not token:
            return redirect('login')

        supabase = get_supabase()
        try:
            user_resp = supabase.auth.get_user(token)
            user = getattr(user_resp, "user", None)
            
            if not user:
                request.session.flush()
                return redirect('login')
            
            user_id = user.id
            role = RolesService.get_user_role(user_id)
            request.session["sb_user_id"] = user_id
            request.session["sb_user_role"] = role or "user"
            
        except Exception as e:
            print("Error Autenticando Supabase:", e)
            request.session.flush()
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped


def require_role(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs):
            token = request.session.get('sb_access_token')
            if not token:
                return redirect('login')

            supabase = get_supabase()
            try:
                user_resp = supabase.auth.get_user(token)
                user = getattr(user_resp, "user", None)
                if not user:
                    request.session.flush()
                    return redirect('login')

                user_id = user.id
                role_resp = (
                    supabase.table("roles_usuario")
                    .select("rol")
                    .eq("usuario_id", user_id)
                    .execute()
                )
                
                if not role_resp.data:
                    return redirect('unauthorized')
                
                user_role = role_resp.data[0].get("rol")

                if user_role != role:
                    return redirect('unauthorized')
                
            except Exception as e:
                print(f"Error occurred: {e}")
                request.session.flush()
                return redirect('login')

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
