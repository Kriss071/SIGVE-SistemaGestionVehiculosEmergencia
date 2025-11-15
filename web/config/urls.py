from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    # path('vehiculos/', include('vehicles.urls')),
    # path('mantencion/', include('maintenance.urls')),
    # path('administracion/', include(('backoffice.urls', 'backoffice'), namespace='backoffice')),
    path('sigve/', include(('apps.sigve.urls', 'sigve'), namespace='sigve')),
    path('taller/', include(('apps.workshop.urls', 'workshop'), namespace='workshop')),
    path('fire-station/', include(('apps.fire_station.urls', 'fire_station'), namespace='fire_station'))
]
