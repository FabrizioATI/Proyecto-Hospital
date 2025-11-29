from django.db import models
from django.utils import timezone


# ============================================================
# ENTIDAD (PERSONAS)
# ============================================================

class Entidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    dni = models.CharField(max_length=15, unique=True)

    def nombre_completo(self):
        return f"{self.nombre} {self.apellidoPaterno} {self.apellidoMaterno}"

    def __str__(self):
        return self.nombre_completo()


# ============================================================
# ROLES
# ============================================================

class Rol(models.Model):
    codigo_rol = models.CharField(max_length=3, unique=True, null=True, blank=True)
    nombre_rol = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_rol


class RolEntidad(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entidad} - {self.rol}"


# ============================================================
# MEDICOS / ESPECIALIDADES
# ============================================================

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    # Capacidad máxima de cupos por hora para esta especialidad (ej: 10)
    capacidad_por_hora = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.nombre


class DoctorDetalle(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    nro_colegiatura = models.CharField(max_length=50, unique=True)
    # Opcional: cupos por doctor (si no se define, se asume sin límite específico)
    cupos_diarios = models.PositiveIntegerField(null=True, blank=True)
    cupos_semanales = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Dr. {self.entidad.nombre} ({self.especialidad.nombre})"


# ============================================================
# HORARIOS DE DOCTOR
# ============================================================

class Horario(models.Model):
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin}"


class DoctorHorario(models.Model):
    doctor = models.ForeignKey(DoctorDetalle, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["doctor", "horario"], name="uq_doctor_horario"),
        ]

    def __str__(self):
        return f"{self.doctor} → {self.horario}"

# ============================================================
# CITA (Atención del paciente)
# ============================================================

class Cita(models.Model):
    CLASIFICACION_CHOICES = [
        ('EMERGENCIA', 'Emergencia'),
        ('ADULTO_MAYOR', 'Adulto Mayor'),
        ('REGULAR', 'Regular'),
    ]

    ESTADO_CHOICES = [
        ('EN_ESPERA', 'En espera'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
        ('NO_SHOW', 'No asistió'),
    ]
    
    TIPO_CITA = [
        ('VIRTUAL', 'Virtual'),
        ('PRESENCIAL', 'Presencial')
    ]

    paciente = models.ForeignKey(
        Entidad, on_delete=models.CASCADE, related_name="citas_paciente"
    )

    doctor = models.ForeignKey(
        Entidad, on_delete=models.CASCADE, related_name="citas_doctor"
    )

    doctor_horario = models.ForeignKey(
        DoctorHorario, on_delete=models.CASCADE, related_name="citas"
    )

    motivo = models.TextField()

    clasificacion = models.CharField(
        max_length=20, choices=CLASIFICACION_CHOICES, default='REGULAR'
    )

    prioridad = models.PositiveSmallIntegerField(default=3)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="EN_ESPERA"
    )
    
    tipo_cita = models.CharField(
        max_length=20, choices=TIPO_CITA, default="PRESENCIAL"
    )

    # Campo para almacenar el EHR ID del paciente
    ehr_id = models.CharField(max_length=50, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.prioridad = {
            'EMERGENCIA': 1,
            'ADULTO_MAYOR': 2,
            'REGULAR': 3,
        }.get(self.clasificacion, 3)

        super().save(*args, **kwargs)

    class Meta:
        ordering = [
            "prioridad",
            "doctor_horario__horario__fecha",
            "doctor_horario__horario__hora_inicio",
            "fecha_creacion"
        ]

    def __str__(self):
        return f"Cita #{self.id} - {self.paciente.nombre_completo()} - {self.clasificacion} - {self.prioridad} - {self.estado}"


# ============================================================
# LISTA DE ESPERA
# ============================================================

class WaitlistItem(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('notificado', 'Notificado'),
        ('aceptado', 'Aceptado'),
        ('expirado', 'Expirado'),
        ('rechazado', 'Rechazado'),
    ]

    CLASIFICACION_CHOICES = Cita.CLASIFICACION_CHOICES
    TIPO_CITA_CHOICES = Cita.TIPO_CITA 

    paciente = models.ForeignKey(
        Entidad, on_delete=models.CASCADE, related_name='waitlist_items'
    )
    doctor_horario = models.ForeignKey(
        DoctorHorario,
        on_delete=models.CASCADE,
        related_name='waitlist_items',
        null=True, blank=True,
    )

    motivo = models.TextField()       
    clasificacion = models.CharField( 
        max_length=20,
        choices=CLASIFICACION_CHOICES,
        default='REGULAR',
    )
    
    tipo_cita = models.CharField(          
        max_length=20,
        choices=TIPO_CITA_CHOICES,
        default='PRESENCIAL',
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    ttl_respuesta_min = models.PositiveIntegerField(default=15)

    class Meta:
        unique_together = ("paciente", "doctor_horario")
        ordering = ["fecha_solicitud"]

    def __str__(self):
        return f"Waitlist: {self.paciente} → {self.doctor_horario or 'SIN HORARIO'}"


# ============================================================
# LISTA DE FERIADOS
# ============================================================

class Holiday(models.Model):
    """Feriados/holidays para controlar disponibilidad por fecha.

    Se guarda solo la fecha (DateField) y un nombre corto opcional.
    """
    fecha = models.DateField(unique=True)
    nombre = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.fecha} - {self.nombre or 'Feriado'}"


# ============================================================
# LISTA DE FERIADOS
# ============================================================


# === EHR / Historia Clínica ===
class HistoriaClinica(models.Model):
    """Historia clínica única por paciente."""
    paciente = models.OneToOneField(
        Entidad, on_delete=models.CASCADE, related_name='historia_clinica'
    )
    # Un identificador legible (ej. HCL-<DNI>), puedes personalizarlo
    numero = models.CharField(max_length=50, unique=True, blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Autogenera numero si no existe (ej. HCL-<DNI>)
        if not self.numero and self.paciente and self.paciente.dni:
            self.numero = f"HCL-{self.paciente.dni}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero or 'HCL'} - {self.paciente.nombre_completo()}"


class EpisodioClinico(models.Model):
    """Episodio ligado a una cita (consulta), internamiento, emergencia, etc."""
    ESTADOS = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
    ]
    TIPO = [
        ('consulta', 'Consulta'),
        ('emergencia', 'Emergencia'),
        ('seguimiento', 'Seguimiento'),
    ]

    historia = models.ForeignKey(
        HistoriaClinica, on_delete=models.CASCADE, related_name='episodios'
    )
    cita = models.OneToOneField(
        Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='episodio'
    )

    tipo = models.CharField(max_length=20, choices=TIPO, default='consulta')
    motivo = models.TextField(blank=True, null=True)

    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto')
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(blank=True, null=True)

    def cerrar(self):
        self.estado = 'cerrado'
        self.fin = timezone.now()
        self.save(update_fields=['estado', 'fin'])

    def __str__(self):
        base = f"Episodio #{self.id} - {self.historia.numero}"
        return f"{base} ({self.tipo}, {self.estado})"


class NotaEvolucion(models.Model):
    """Notas/Registros dentro del episodio (anamnesis, evolución, indicaciones)."""
    episodio = models.ForeignKey(
        EpisodioClinico, on_delete=models.CASCADE, related_name='notas'
    )
    autor = models.ForeignKey(
        Entidad, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_autor'
    )  # normalmente el doctor
    titulo = models.CharField(max_length=150, blank=True, null=True)
    contenido = models.TextField()  # texto libre (anamnesis, hallazgos, plan)
    signos_vitales = models.JSONField(blank=True, null=True)  # opcional: {temp, fc, pa, spo2, ...}
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota #{self.id} - Episodio {self.episodio_id}"


# ============================================================
# NOTIFICACIONES SMS (RF12)
# ============================================================

class SMSNotification(models.Model):
    """
    Registro de notificaciones SMS enviadas a pacientes.
    Almacena intentos y estado de entrega para auditoría (RF12).
    """
    TIPO_CHOICES = [
        ('recordatorio', 'Recordatorio'),
        ('instrucciones', 'Instrucciones'),
        ('llamado', 'Llamado a ingreso'),
    ]

    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('pendiente', 'Pendiente'),
    ]

    cita = models.ForeignKey(
        Cita, on_delete=models.CASCADE, related_name='sms_notifications'
    )
    paciente = models.ForeignKey(
        Entidad, on_delete=models.CASCADE, related_name='sms_notificaciones'
    )

    telefono = models.CharField(max_length=20, help_text="Número de teléfono destino")
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='recordatorio'
    )

    mensaje = models.TextField(help_text="Contenido del SMS")

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='pendiente'
    )

    # Identificadores de Twilio para tracking
    sid = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="SID de Twilio para tracking"
    )

    intento = models.PositiveSmallIntegerField(default=1, help_text="Número de intento")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)

    respuesta_twilio = models.TextField(
        blank=True, null=True, help_text="Respuesta JSON de Twilio"
    )

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"SMS #{self.id} - {self.paciente.nombre_completo()} ({self.estado})"


class NotificationPreference(models.Model):

    LANG_CHOICES = [
        ("es", "Español"),
        ("qu", "Quechua"),
    ]

    user = models.OneToOneField(
        Entidad,
        on_delete=models.CASCADE,
        related_name="notif_pref"
    )

    sms_consent = models.BooleanField(default=False)
    sms_language = models.CharField(
        max_length=5,
        choices=LANG_CHOICES,
        default="es"
    )

    consent_updated_at = models.DateTimeField(auto_now=True)  # trazabilidad

    def __str__(self):
        return f"{self.user.dni} | consent={self.sms_consent} | lang={self.sms_language}"