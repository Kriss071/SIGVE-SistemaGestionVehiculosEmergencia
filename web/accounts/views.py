from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from .client.supabase_client import get_supabase
from .decorators import require_supabase_login
from .services.auth_service import AuthService
from .services.roles_services import RolesService


@require_supabase_login
def home_view(request):
    return render(
        request, "accounts/home.html", {"email": request.session.get("sb_user_email")}
    )


def login_view(request):
    if request.session.get("sb_access_token"):
        return redirect("vehicle_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            session, error = AuthService.login(
                form.cleaned_data["email"], form.cleaned_data["password"]
            )
            if error or not session:
                messages.error(request, error or "Error desconocido.")
                return render(request, "accounts/login.html", {"form": form})

            request.session.flush()
            request.session["sb_access_token"] = session.access_token
            request.session["sb_refresh_token"] = session.refresh_token
            request.session["sb_user_email"] = form.cleaned_data["email"]
            request.session.set_expiry(0)

            user_id = session.user.id
            user_role = RolesService.get_user_role(user_id)
            
            request.session["sb_user_id"] = user_id
            request.session["sb_user_role"] = user_role or "user"

            messages.success(request, "¡Sesión iniciada!")
            return redirect("vehicle_list")
    else:
        form = LoginForm()

    return render(request, "accounts/login_2.html", {"form": form})


def logout_view(request):
    AuthService.logout()
    request.session.flush()
    messages.info(request, "Sesión cerrada.")
    return redirect("login")
