
from django.shortcuts import render, redirect, get_object_or_404
from database.models import Entidad, Especialidad, DoctorDetalle, DoctorHorario, Cita, WaitlistItem
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import services
from .notifier import send_waitlist_offer_email_test
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .services import solicitar_cita, get_doctores_con_horario
from database.models import (
    Entidad, Especialidad, DoctorDetalle,
    DoctorHorario, Cita, WaitlistItem
)


#Index
def index(request):
    return render(request, "home/index.html")

# CRUD de Citas
def lista_citas_paciente(request, paciente_id):
    citas = Cita.objects.select_related(
        "paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario"
    ).filter(paciente_id=paciente_id)

    return render(request, "citas/lista_citas.html", {"citas": citas})

def editar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    errors = {}
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad=cita.doctor_horario.doctor.especialidad)
    horarios = DoctorHorario.objects.filter(doctor=cita.doctor_horario.doctor).select_related("horario")

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        tipo_cita = request.POST.get("tipo_cita")  # <-- viene del select

        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        if tipo_cita not in ["PRESENCIAL", "VIRTUAL"]:
            errors["tipo_cita"] = "Debe seleccionar una modalidad válida."

        if not errors:
            cita.motivo = motivo
            cita.tipo_cita = tipo_cita  # <-- AQUÍ se guarda
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

def checkin_view(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    # Registrar el check-in como antes
    services.registrar_checkin(cita)

    # Vincular con EHR (simulado)
    if not cita.ehr_id:
        ehr_id = f"EHR-{cita.paciente.dni}"
        cita.ehr_id = ehr_id
        cita.estado = "confirmada"  # marcamos la cita como confirmada al hacer check-in
        cita.save()

        messages.success(
            request,
            f"Cita vinculada exitosamente con el registro EHR del paciente: {ehr_id}"
        )
    else:
        messages.info(request, f"La cita ya estaba vinculada con el ID EHR: {cita.ehr_id}")

    # Mostrar resultado
    return render(request, 'citas/checkin_exitoso.html', {'cita': cita})

def cancelar_cita_view(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    services.cancelar_y_ofertar(cita)

    # if next_wait:
    #     accept_url = request.build_absolute_uri(
    #         reverse('aceptar_waitlist', args=[next_wait.id])
    #     )

    #     resultado = send_waitlist_offer_email_test(next_wait, accept_url)
    #     print("-->RESULTADO EMAIL: ", resultado)

    #     messages.info(
    #         request,
    #         mark_safe(
    #             'Se ha ofrecido el cupo al siguiente en lista de espera. '
    #             '<br>Revisa la consola o el correo para verificar el envío de la notificación.'
    #         )
    #     )
    # else:
    #     messages.info(request, 'Cita cancelada y sin lista de espera pendiente.')

    return redirect('lista_citas_paciente', paciente_id=cita.paciente.id)
 
def registrar_cita_paciente(request, paciente_id):
    paciente = get_object_or_404(Entidad, id=paciente_id)
    errors = {}

    # ----------- GET: cargar combos --------------
    especialidades = Especialidad.objects.all()

    especialidad_id = request.GET.get("especialidad")
    selected_doc = request.GET.get("doctor")

    doctores = (
        get_doctores_con_horario(especialidad_id)
        if especialidad_id else []
    )

    # ----------- POST: registrar solicitud --------------
    if request.method == "POST":

        doctor_id = request.POST.get("doctor_id")       # aquí pondrás id de DoctorDetalle
        clasificacion = request.POST.get("clasificacion") or "REGULAR"
        tipo_cita = request.POST.get("tipo_cita") or "PRESENCIAL" 
        motivo = request.POST.get("motivo")

        if not doctor_id:
            errors["doctor_id"] = "Debe seleccionar un médico."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        if errors:
            return render(request, "citas/registrar_cita.html", {
                "especialidades": especialidades,
                "paciente": paciente,
                "doctores": doctores,
                "errors": errors,
                "selected_esp": especialidad_id,
                "selected_doc": selected_doc,
            })

        # doctor_id es DoctorDetalle.id
        doctor_detalle = get_object_or_404(DoctorDetalle, id=doctor_id)

        # ---- VALIDACIÓN ANTI-ABUSO ----
        # Verificar si el paciente ya tiene 2 citas activas para esta especialidad
        especialidad = doctor_detalle.especialidad

        citas_activas = Cita.objects.filter(
            paciente=paciente,
            doctor_horario__doctor__especialidad=especialidad,
            estado__in=["pendiente", "confirmada"]  # Ajusta según tus estados válidos
        ).count()

        if citas_activas >= 2:
            messages.error(request, "Límite de citas activas alcanzado para esta especialidad")
            return redirect("lista_citas_paciente", paciente_id=paciente_id)
        # --------------------------------


        # 1) Registrar en la waitlist
        solicitar_cita(
            paciente=paciente,
            doctor_detalle=doctor_detalle,
            clasificacion=clasificacion,
            tipo_cita=tipo_cita,
            motivo=motivo,
        )

        # 2) Mensaje
        messages.success(
            request,
            "Tu solicitud de cita ha sido registrada. "
            "El sistema asignará el horario automáticamente según tu prioridad."
        )

        return redirect("lista_citas_paciente", paciente_id=paciente_id)

    # ----------- RENDER GET --------------
    return render(request, "citas/registrar_cita.html", {
        "especialidades": especialidades,
        "paciente": paciente,
        "doctores": doctores,
        "errors": errors,
        "selected_esp": int(especialidad_id) if especialidad_id else None,
        "selected_doc": int(selected_doc) if selected_doc else None,
    })