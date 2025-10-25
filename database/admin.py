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


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'estado', 'hora_llegada')
    list_filter = ('estado',)
    search_fields = (
        'cita__paciente__nombres', 'cita__paciente__apellidos',
        'cita__doctor_horario__doctor__entidad__nombres', 'cita__doctor_horario__doctor__entidad__apellidos'
    )

admin.site.register(Entidad)
admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(RolEntidad)
admin.site.register(Especialidad)
admin.site.register(DoctorDetalle)
admin.site.register(Horario)
admin.site.register(DoctorHorario)
admin.site.register(Cita)
