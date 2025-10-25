from django.db import models
from django.db.models import Q
from django.utils import timezone

class Entidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidoPaterno = models.CharField(max_length=100)
    apellidoMaterno = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=128)  # recomendable usar hash
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidoPaterno} {self.apellidoMaterno}"

    def nombre_completo(self):
        return f"{self.nombre} {self.apellidoPaterno} {self.apellidoMaterno}".strip()

class Usuario(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)

    def __str__(self):
        return f"Usuario: {self.entidad.correo}"

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)  # admin, doctor, paciente

    def __str__(self):
        return self.nombre_rol

class RolEntidad(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entidad} - {self.rol}"

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class DoctorDetalle(models.Model):
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)  # Solo si tiene rol doctor
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    nro_colegiatura = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Dr. {self.entidad.nombre} ({self.especialidad.nombre})"

class Horario(models.Model):
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.fecha} {self.hora_inicio}-{self.hora_fin}"

class DoctorHorario(models.Model):
    doctor = models.ForeignKey(DoctorDetalle, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.doctor} - {self.horario}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["doctor", "horario"], name="uq_doctor_horario_exact"),
        ]

class Cita(models.Model):
    paciente = models.ForeignKey('Entidad', on_delete=models.CASCADE, related_name="citas")
    doctor_horario = models.ForeignKey('DoctorHorario', on_delete=models.CASCADE, related_name="citas")
    estado = models.CharField(
        max_length=20,
        choices=[
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("cancelada", "Cancelada"),
            ("atendida", "Atendida"),
        ],
        default="pendiente"
    )
    tipo = models.CharField(
        max_length=20,
        choices=[("presencial", "Presencial"), ("virtual", "Virtual")],
        default="presencial",
        null=True,
        blank=True,
    )
    motivo = models.TextField()

    def __str__(self):
        return f"Cita {self.id} - {self.paciente} con {self.doctor_horario.doctor}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor_horario"],
                condition=Q(estado__in=["pendiente", "confirmada"]),
                name="uq_cita_slot_activo_por_doctor_horario",
            )
        ]
        
class WaitlistItem(models.Model):
    ESTADOS = (
    ('pendiente', 'Pendiente'),
    ('notificado', 'Notificado'),
    ('aceptado', 'Aceptado'),
    ('expirado', 'Expirado'),
    ('rechazado', 'Rechazado'),
    )


    paciente = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name='waitlist_items')
    doctor_horario = models.ForeignKey(DoctorHorario, on_delete=models.CASCADE, related_name='waitlist_items')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    ttl_respuesta_min = models.PositiveIntegerField(default=15) # ventana para aceptar cupo liberado


    class Meta:
        indexes = [
        models.Index(fields=['doctor_horario', 'fecha_solicitud']),
        ]
        unique_together = (
        ('paciente', 'doctor_horario'),
        )


    def __str__(self):
        return f"Waitlist({self.paciente_id} -> DH:{self.doctor_horario_id}, {self.estado})"

class CheckIn(models.Model):
    ESTADOS = (
    ('en_espera', 'En espera'),
    ('atendiendo', 'Atendiendo'),
    ('atendido', 'Atendido'),
    ('no_show', 'No show'),
    )


    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='checkin')
    hora_llegada = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='en_espera')


    class Meta:
        indexes = [
        models.Index(fields=['hora_llegada']),
        ]


    def __str__(self):
        return f"CheckIn(Cita:{self.cita_id}, {self.estado})"