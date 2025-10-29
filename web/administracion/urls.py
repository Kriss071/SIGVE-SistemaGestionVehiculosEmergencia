

from django.urls import path
from . import views 

urlpatterns = [
    path('usuarios/', views.user_list_view, name='listado_user'),
    path('detail/', views.user_detail_api, name='user_detail_api'),
    

]