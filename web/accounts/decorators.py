from functools import wraps
from django.http import HttpRequest
from django.shortcuts import redirect
from accounts.supabase_client import get_supabase


def require_supabase_login(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        token = request.session.get('sb_access_token')
        if not token:
            return redirect('login')

        supabase = get_supabase()
        try:
            user_resp = supabase.auth.get_user(token)
            if not getattr(user_resp, "user", None):
                request.session.flush()
                return redirect('login')
        except Exception:
            request.session.flush()
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped

