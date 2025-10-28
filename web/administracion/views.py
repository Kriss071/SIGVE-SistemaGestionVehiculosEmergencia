

from django.shortcuts import render
from django.contrib import messages

# 1. Importamos el decorador de la app 'accounts'
from accounts.decorators import require_role

# 2. Importamos el NUEVO servicio
from .services.user_service import UserService

# 3. Protegemos la vista y creamos la función

def user_list_view(request):
    
    service = UserService()
    users, error = service.list_users_with_roles()
    
    if error:
        messages.error(request, f"Error al cargar usuarios: {error}")
        
    context = {
        'users': users
    }
    
    # 4. Renderizamos el template
    return render(request, 'administracion/listado_user.html', context)