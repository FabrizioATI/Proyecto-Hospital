from django.contrib import admin
from .models import *

@admin.register(WaitlistItem)
class WaitlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'doctor_horario', 'estado', 'fecha_solicitud', 'ttl_respuesta_min')
    list_filter = ('estado',)
    search_fields = (
        'paciente__nombres', 'paciente__apellidos',
        'doctor_horario__doctor__entidad__nombres', 'doctor_horario__doctor__entidad__apellidos'
    )

admin.site.register(Entidad)
admin.site.register(Rol)
admin.site.register(RolEntidad)
admin.site.register(Especialidad)
admin.site.register(DoctorDetalle)
admin.site.register(Horario)
admin.site.register(DoctorHorario)
admin.site.register(Cita)
admin.site.register(Holiday)
