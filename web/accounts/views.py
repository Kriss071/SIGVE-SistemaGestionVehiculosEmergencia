from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from functools import wraps
from .forms import LoginForm
from supabase_client import get_supabase


def require_supabase_login(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        token = request.session.get('sb_access_token')
        if not token:
            return redirect('login')

        supabase = get_supabase()
        try:
           
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                raise Exception("Token inválido")
        except Exception:
            request.session.flush()
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return _wrapped


def login_view(request: HttpRequest) -> HttpResponse:
   
    if request.session.get('sb_access_token'):
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            supabase = get_supabase()

            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password,
                })

    
                if not getattr(res, "session", None) or not getattr(res.session, "access_token", None):
                    messages.error(request, "Credenciales inválidas.")
                    return render(request, 'auth_templates/login.html', {'form': form})


                request.session.flush()
                request.session['sb_access_token'] = res.session.access_token
                request.session['sb_refresh_token'] = res.session.refresh_token
                request.session['sb_user_email'] = email
                request.session.set_expiry(0)  

                messages.success(request, "¡Sesión iniciada!")
                return redirect('home')

            except Exception:

                messages.error(request, "No pudimos iniciar sesión. Verifica email y contraseña.")
                return render(request, 'auth_templates/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'auth_templates/login.html', {'form': form})


@require_supabase_login
def home_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'auth_templates/home.html', {
        'email': request.session.get('sb_user_email')
    })


def logout_view(request: HttpRequest) -> HttpResponse:
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    request.session.flush()
    messages.info(request, "Sesión cerrada.")
    return redirect('login')
