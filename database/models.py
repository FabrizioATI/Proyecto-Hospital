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

    def __str__(self):
        return self.nombre


class DoctorDetalle(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    nro_colegiatura = models.CharField(max_length=50, unique=True)

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