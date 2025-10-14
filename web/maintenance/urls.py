from django.urls import path
from . import views

urlpatterns = [
    path('', views.maintenance_list_view, name="maintenance_list")
]
