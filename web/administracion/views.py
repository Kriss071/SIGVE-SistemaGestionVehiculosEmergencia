



# 1. Importamos el decorador de la app 'accounts'
from accounts.decorators import require_role

# 2. Importamos el NUEVO servicio
from .services.user_service import UserService

# 3. Protegemos la vista y creamos la función


from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound

from accounts.decorators import require_role,require_supabase_login




#@require_role("administrador")     -->esto se activara cuando se solucione el problema de roles
def user_list_view(request):
    
    service = UserService()
    users, error = service.list_users_with_roles()
    
    if error:
        messages.error(request, f"Error al cargar usuarios: {error}")
        
    context = {
        'users': users
    }
    

    return render(request, 'administracion/listado_user.html', context)
def user_list_view(request):
    
    service = UserService()
    users, error = service.list_users_with_roles()
    
    if error:
        messages.error(request, f"Error al cargar usuarios: {error}")
        
    context = {
        'users': users
    }
    
   
    return render(request, 'administracion/listado_user.html', context)
@require_supabase_login 
def user_detail_api(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponseBadRequest("Falta el parámetro 'user_id'")

    service = UserService() 
    user_details, error_msg = service.get_user_details(user_id) 

    if error_msg:
        return HttpResponseNotFound(f"Error al obtener usuario: {error_msg}")
    
    if not user_details:
         return HttpResponseNotFound("Usuario no encontrado")

    return JsonResponse({"user": user_details})