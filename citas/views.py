from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad, DoctorHorario, Horario
from django.contrib.auth import logout as django_logout 
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad
from .models import Cita, DoctorHorario 

#Index
def index(request):
    return render(request, "home/index.html")

# CRUD de Citas
def lista_citas_paciente(request, paciente_id):
    citas = Cita.objects.select_related(
        "paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario"
    ).filter(paciente_id=paciente_id)

    return render(request, "citas/lista_citas.html", {"citas": citas})

def registrar_cita_paciente(request, paciente_id):
    paciente = get_object_or_404(Entidad, id=paciente_id)
    errors = {}

    especialidad_id = request.GET.get("especialidad")
    doctor_id = request.GET.get("doctor")

    if request.method == "POST":
        doctor_horario_id = request.POST.get("doctor_horario")
        motivo = request.POST.get("motivo")

        if not doctor_horario_id:
            errors["doctor_horario"] = "Debe seleccionar un horario de doctor."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        if not errors:
            doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
            Cita.objects.create(
                paciente=paciente,               # ← El paciente viene de la sesión
                doctor_horario=doctor_horario,
                motivo=motivo,
                estado="pendiente",
            )
            # messages.success(request, "Cita registrada correctamente.")
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad_id=especialidad_id) if especialidad_id else []
    horarios = DoctorHorario.objects.filter(doctor_id=doctor_id).select_related("horario") if doctor_id else []

    return render(request, "citas/registrar_cita.html", {
        "paciente": paciente,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "errors": errors,
        "selected_esp": int(especialidad_id) if especialidad_id else None,
        "selected_doc": int(doctor_id) if doctor_id else None,
    })

def editar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    errors = {}

    # Para mostrar las listas
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad=cita.doctor_horario.doctor.especialidad)
    horarios = DoctorHorario.objects.filter(doctor=cita.doctor_horario.doctor).select_related("horario")

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        else:
            cita.motivo = motivo
            cita.save()
            # messages.success(request, "Cita actualizada correctamente.")
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    return render(request, "citas/editar_cita.html", {
        "cita": cita,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "selected_esp": cita.doctor_horario.doctor.especialidad.id,
        "selected_doc": cita.doctor_horario.doctor.id,
        "errors": errors,
    })

def eliminar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    cita.delete()
    # messages.success(request, "Cita eliminada correctamente.")
    return redirect("lista_citas_paciente", paciente_id=paciente_id)

def lista_citas_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorDetalle, entidad_id=doctor_id)
    citas = Cita.objects.filter(doctor_horario__doctor=doctor).select_related(
        "paciente", "doctor_horario__horario"
    ).order_by("doctor_horario__horario__fecha", "doctor_horario__horario__hora_inicio")

    return render(request, "citas/lista_citas.html", {
        "citas": citas,
        "doctor": doctor,
        "tipo_usuario": "doctor"
    })


