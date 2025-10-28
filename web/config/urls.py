from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('vehiculos/', include('vehicles.urls')),
    path('mantencion/', include('maintenance.urls')),
    path('administracion/', include('administracion.urls')),
]
