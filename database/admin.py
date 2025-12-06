from django.contrib import admin
from .models import (
    WaitlistItem,
    Entidad,
    Rol,
    RolEntidad,
    Especialidad,
    DoctorDetalle,
    Horario,
    DoctorHorario,
    Cita,
    Holiday,
    HistoriaClinica,
    EpisodioClinico,
    NotaEvolucion,
    SMSNotification,
    Derivacion
)

# ================================================
#   ADMIN: WaitlistItem
# ================================================
@admin.register(WaitlistItem)
class WaitlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'doctor_horario', 'estado',
                    'fecha_solicitud', 'ttl_respuesta_min')
    list_filter = ('estado',)
    search_fields = (
        'paciente__nombres', 'paciente__apellidos',
        'doctor_horario__doctor__entidad__nombres',
        'doctor_horario__doctor__entidad__apellidos'
    )


# ================================================
#   ADMIN: Especialidad (modificada)
# ================================================
@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "capacidad_por_hora", "requiere_derivacion")
    list_editable = ("requiere_derivacion",)
    search_fields = ("nombre",)


# ================================================
#   ADMIN: Derivacion (nuevo)
# ================================================
@admin.register(Derivacion)
class DerivacionAdmin(admin.ModelAdmin):
    list_display = ("id", "paciente", "especialidad", "valido", "fecha_emision")
    list_filter = ("especialidad", "valido")
    search_fields = (
        "paciente__dni",
        "paciente__nombre",
        "paciente__apellidoPaterno",
        "paciente__apellidoMaterno",
    )


# ================================================
#   REGISTROS BÁSICOS SIN PERSONALIZAR
# ================================================
admin.site.register(Entidad)
admin.site.register(Rol)
admin.site.register(RolEntidad)
admin.site.register(DoctorDetalle)
admin.site.register(Horario)
admin.site.register(DoctorHorario)
admin.site.register(Cita)
admin.site.register(Holiday)
admin.site.register(HistoriaClinica)
admin.site.register(EpisodioClinico)
admin.site.register(NotaEvolucion)


# ================================================
#   ADMIN: SMSNotification
# ================================================
@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'telefono', 'tipo', 'estado',
                    'fecha_creacion', 'intento')
    list_filter = ('estado', 'tipo', 'fecha_creacion')
    search_fields = ('paciente__nombre', 'paciente__apellidoPaterno',
                     'telefono', 'sid')
    readonly_fields = ('fecha_creacion', 'fecha_envio', 'fecha_entrega',
                       'sid', 'respuesta_twilio')

    fieldsets = (
        ('Información General', {
            'fields': ('paciente', 'cita', 'telefono')
        }),
        ('Notificación', {
            'fields': ('tipo', 'mensaje', 'estado')
        }),
        ('Tracking de Twilio', {
            'fields': ('sid', 'intento', 'respuesta_twilio')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_envio', 'fecha_entrega')
        }),
    )
