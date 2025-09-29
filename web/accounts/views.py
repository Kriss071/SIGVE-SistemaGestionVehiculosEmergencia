from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .forms import LoginForm
from .supabase_client import get_supabase
from .decorators import require_supabase_login
from supabase import AuthApiError
  
@require_supabase_login
def home_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'accounts/home.html', {
        'email': request.session.get('sb_user_email')
    })

  
def login_view(request: HttpRequest) -> HttpResponse:
    if request.session.get('sb_access_token'):
        return redirect('vehicle_list')

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
                    return render(request, 'accounts/login.html', {'form': form})

                request.session.flush()
                request.session['sb_access_token'] = res.session.access_token
                request.session['sb_refresh_token'] = res.session.refresh_token
                request.session['sb_user_email'] = email
                request.session.set_expiry(0)  

                messages.success(request, "¡Sesión iniciada!")
                return redirect('vehicle_list')

            except AuthApiError as e:
                messages.error(request, f"Error al iniciar sesión: {str(e)}")
                return render(request, 'accounts/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request: HttpRequest) -> HttpResponse:
    try:
        get_supabase().auth.sign_out()
    except Exception as e:
        print(f"Error al cerrar sesión en Supabase: {e}")
    request.session.flush()
    messages.info(request, "Sesión cerrada.")
    return redirect('login')
