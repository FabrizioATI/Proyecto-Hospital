from django.shortcuts import render, redirect, get_object_or_404
from database.models import Entidad, Especialidad, DoctorDetalle, DoctorHorario, Cita, TipoCita


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
    from database.models import TipoCita  # Import local para evitar dependencias circulares
    paciente = get_object_or_404(Entidad, id=paciente_id)
    errors = {}

    # Filtros GET
    especialidad_id = request.GET.get("especialidad")
    doctor_id = request.GET.get("doctor")

    # Si se envía el formulario (POST)
    if request.method == "POST":
        doctor_horario_id = request.POST.get("doctor_horario")
        motivo = request.POST.get("motivo")
        tipo_cita_id = request.POST.get("tipo_cita")
        modalidad = request.POST.get("tipo")

        # Validaciones
        if not doctor_horario_id:
            errors["doctor_horario"] = "Debe seleccionar un horario de doctor."
        if not tipo_cita_id:
            errors["tipo_cita"] = "Debe seleccionar un tipo de cita."
        if not modalidad:
            errors["tipo"] = "Debe seleccionar la modalidad de la cita."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        # Si no hay errores, se guarda la cita
        if not errors:
            doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
            tipo_cita = TipoCita.objects.get(id=tipo_cita_id)
            Cita.objects.create(
                paciente=paciente,
                doctor_horario=doctor_horario,
                motivo=motivo,
                tipo_cita=tipo_cita,
                tipo=modalidad,
                estado="pendiente",
            )
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    # Datos para los selects dinámicos
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad_id=especialidad_id) if especialidad_id else []
    horarios = DoctorHorario.objects.filter(doctor_id=doctor_id).select_related("horario") if doctor_id else []
    tipos_cita = TipoCita.objects.all()

    return render(request, "citas/registrar_cita.html", {
        "paciente": paciente,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "tipos_cita": tipos_cita,
        "errors": errors,
        "selected_esp": int(especialidad_id) if especialidad_id else None,
        "selected_doc": int(doctor_id) if doctor_id else None,
    })


def editar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    errors = {}
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad=cita.doctor_horario.doctor.especialidad)
    horarios = DoctorHorario.objects.filter(doctor=cita.doctor_horario.doctor).select_related("horario")
    tipos_cita = TipoCita.objects.all()  # 🔹 Agregado aquí

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        tipo_cita_id = request.POST.get("tipo_cita")
        tipo = request.POST.get("tipo")

        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        if not tipo_cita_id:
            errors["tipo_cita"] = "Debe seleccionar un tipo de cita."
        if not tipo:
            errors["tipo"] = "Debe seleccionar una modalidad."

        if not errors:
            cita.motivo = motivo
            cita.tipo_cita_id = tipo_cita_id
            cita.tipo = tipo
            cita.save()
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    return render(request, "citas/editar_cita.html", {
        "cita": cita,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "selected_esp": cita.doctor_horario.doctor.especialidad.id,
        "selected_doc": cita.doctor_horario.doctor.id,
        "errors": errors,
        "tipos_cita": tipos_cita,  # 🔹 Y también aquí en el contexto
    })

def eliminar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    cita.delete()
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


