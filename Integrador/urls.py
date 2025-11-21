from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('administrador.urls')),
    path('', include('login.urls')),
    path('', include('citas.urls')),
    path('', include('horarios.urls')),
    path('', include('medico.urls')),
    path('', include('paciente.urls'))
]
