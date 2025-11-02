from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicle_list_view, name='vehicle_list'),
    path('add/', views.add_vehicle_view, name='add_vehicle'),
    path('search/', views.vehicle_search_api, name='vehicle_search_api'),
    path('detail/', views.vehicle_detail_api, name='vehicle_detail_api'),
    path('delete/', views.delete_vehicle_api, name='delete_vehicle_api'),
    path('update/', views.update_vehicle_api, name='update_vehicle_api')
]