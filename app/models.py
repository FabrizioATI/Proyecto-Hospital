from django.db import models


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


class Cita(models.Model):
    paciente = models.ForeignKey(Entidad, on_delete=models.CASCADE, related_name="citas")
    doctor_horario = models.ForeignKey(DoctorHorario, on_delete=models.CASCADE)
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
    motivo = models.TextField()

    def __str__(self):
        return f"Cita {self.id} - {self.paciente} con {self.doctor_horario.doctor}"