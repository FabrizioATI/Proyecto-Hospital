from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad
from .models import Cita, DoctorHorario 


def lista_medicos(request):
    medicos = DoctorDetalle.objects.select_related("entidad", "especialidad").all()
    return render(request, "doctor/lista_medicos.html", {"medicos": medicos})

def eliminar_medico(request, pk):
    doctor = get_object_or_404(DoctorDetalle, pk=pk)
    entidad = doctor.entidad
    doctor.delete()
    entidad.delete()  # 👈 elimina también la entidad asociada
    return redirect("lista_medicos")

def registrar_medico(request):
    errors = {}
    if request.method == "POST":
        # Datos de la Entidad
        nombre = request.POST.get("nombre")
        apellidoPaterno = request.POST.get("apellidoPaterno")
        apellidoMaterno = request.POST.get("apellidoMaterno")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        telefono = request.POST.get("telefono")
        dni = request.POST.get("dni")

        especialidad_id = request.POST.get("especialidad")
        nro_colegiatura = request.POST.get("nro_colegiatura")

        # 🔹 Validaciones
        if Entidad.objects.filter(dni=dni).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if DoctorDetalle.objects.filter(nro_colegiatura=nro_colegiatura).exists():
            errors["nro_colegiatura"] = "Este número de colegiatura ya está registrado."

        if not errors:
            # Crear entidad
            entidad = Entidad.objects.create(
                nombre=nombre,
                apellidoPaterno=apellidoPaterno,
                apellidoMaterno=apellidoMaterno,
                correo=correo,
                contraseña=contraseña,  # lo ideal es usar hash
                telefono=telefono,
                dni=dni,
            )

            # Crear doctor
            especialidad = Especialidad.objects.get(id=especialidad_id)
            DoctorDetalle.objects.create(
                entidad=entidad,
                especialidad=especialidad,
                nro_colegiatura=nro_colegiatura,
            )

            # Asignar rol "doctor"
            rol_doctor, created = Rol.objects.get_or_create(nombre_rol="doctor")
            RolEntidad.objects.create(entidad=entidad, rol=rol_doctor)

            messages.success(request, "Médico registrado correctamente.")
            return redirect("lista_medicos")

    # Si es GET o hubo errores
    especialidades = Especialidad.objects.all()
    return render(
        request,
        "doctor/registrar_medicos.html",
        {"especialidades": especialidades, "errors": errors},
    )

def editar_medico(request, pk):
    doctor = get_object_or_404(DoctorDetalle, pk=pk)
    errors = {}

    if request.method == "POST":
        dni = request.POST.get("dni")
        nro_colegiatura = request.POST.get("nro_colegiatura")

        # 🔹 Validaciones (excluyendo al mismo doctor que estamos editando)
        if Entidad.objects.filter(dni=dni).exclude(id=doctor.entidad.id).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if DoctorDetalle.objects.filter(nro_colegiatura=nro_colegiatura).exclude(id=doctor.id).exists():
            errors["nro_colegiatura"] = "Este número de colegiatura ya está registrado."

        if not errors:
            # Actualizar entidad
            doctor.entidad.nombre = request.POST.get("nombre")
            doctor.entidad.apellidoPaterno = request.POST.get("apellidoPaterno")
            doctor.entidad.apellidoMaterno = request.POST.get("apellidoMaterno")
            doctor.entidad.correo = request.POST.get("correo")
            doctor.entidad.telefono = request.POST.get("telefono")
            doctor.entidad.dni = dni
            doctor.entidad.save()

            # Actualizar detalles del doctor
            especialidad_id = request.POST.get("especialidad")
            doctor.especialidad = Especialidad.objects.get(id=especialidad_id)
            doctor.nro_colegiatura = nro_colegiatura
            doctor.save()

            messages.success(request, "Médico actualizado correctamente.")
            return redirect("lista_medicos")

    especialidades = Especialidad.objects.all()
    return render(
        request,
        "doctor/editar_medico.html",
        {"doctor": doctor, "especialidades": especialidades, "errors": errors},
    )




# CRUD de Citas

def lista_citas(request):
    citas = Cita.objects.select_related("paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario").all()
    return render(request, "citas/lista_citas.html", {"citas": citas})


def registrar_cita(request):
    errors = {}
    if request.method == "POST":
        paciente_id = request.POST.get("paciente")
        doctor_horario_id = request.POST.get("doctor_horario")
        estado = request.POST.get("estado")
        motivo = request.POST.get("motivo")

        # Validaciones
        if not paciente_id:
            errors["paciente"] = "Debe seleccionar un paciente."
        if not doctor_horario_id:
            errors["doctor_horario"] = "Debe seleccionar un horario de doctor."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        if not errors:
            paciente = Entidad.objects.get(id=paciente_id)
            doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)

            Cita.objects.create(
                paciente=paciente,
                doctor_horario=doctor_horario,
                estado=estado,
                motivo=motivo,
            )
            messages.success(request, "Cita registrada correctamente.")
            return redirect("lista_citas")

    pacientes = Entidad.objects.all()
    horarios = DoctorHorario.objects.select_related("doctor__entidad", "horario").all()

    return render(
        request,
        "citas/registrar_cita.html",
        {"pacientes": pacientes, "horarios": horarios, "errors": errors},
    )


def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    errors = {}

    if request.method == "POST":
        paciente_id = request.POST.get("paciente")
        doctor_horario_id = request.POST.get("doctor_horario")
        estado = request.POST.get("estado")
        motivo = request.POST.get("motivo")

        if not errors:
            cita.paciente = Entidad.objects.get(id=paciente_id)
            cita.doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
            cita.estado = estado
            cita.motivo = motivo
            cita.save()
            messages.success(request, "Cita actualizada correctamente.")
            return redirect("lista_citas")

    pacientes = Entidad.objects.all()
    horarios = DoctorHorario.objects.select_related("doctor__entidad", "horario").all()

    return render(
        request,
        "citas/editar_cita.html",
        {"cita": cita, "pacientes": pacientes, "horarios": horarios, "errors": errors},
    )


def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    cita.delete()
    messages.success(request, "Cita eliminada correctamente.")
    return redirect("lista_citas")
