from django.contrib import admin
from .models import *

admin.site.register(Entidad)
admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(RolEntidad)
admin.site.register(Especialidad)
admin.site.register(DoctorDetalle)
admin.site.register(Horario)
admin.site.register(DoctorHorario)
admin.site.register(Cita)
admin.site.register(Holiday)