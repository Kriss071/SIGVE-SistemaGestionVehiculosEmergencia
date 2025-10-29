from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('roles/', views.role_list_view, name='role_list'),
]