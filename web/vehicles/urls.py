from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list_view, name='vehicle_list'),
    path('add/', views.add_vehicle_view, name='add_vehicle'),
    path('search/', views.vehicle_search_api, name='vehicle_search_api')
]