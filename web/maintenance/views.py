from django.shortcuts import render
from accounts.decorators import require_supabase_login

@require_supabase_login
def maintenance_list_view(request):
    return render(request, "maintenance/maintenance_list.html")
