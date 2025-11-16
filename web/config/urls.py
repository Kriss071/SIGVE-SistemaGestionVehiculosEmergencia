from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('sigve/', include(('apps.sigve.urls', 'sigve'), namespace='sigve')),
    path('taller/', include(('apps.workshop.urls', 'workshop'), namespace='workshop')),
    path('fire-station/', include(('apps.fire_station.urls', 'fire_station'), namespace='fire_station'))
]
