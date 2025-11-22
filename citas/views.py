
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
    # Filtra las citas del paciente y ordena por fecha de creación (más recientes primero)
    citas = Cita.objects.select_related(
        "paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario"
    ).filter(paciente_id=paciente_id).order_by('-fecha_creacion')  # Ordenar por la fecha de creación

    # Puedes agregar más filtros aquí si es necesario, por ejemplo, solo citas confirmadas:
    # citas = citas.filter(estado='confirmada')

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

    # Verificar si la cita ya fue atendida
    if cita.estado != "ATENDIDA":  # Si la cita no ha sido atendida previamente
        # Registrar el check-in (puede incluir alguna lógica adicional, como el tiempo de llegada)
        services.registrar_checkin(cita)
        print(f"Check-in realizado para la cita #{cita.id}")

        # Vinculación con EHR (simulado)
        if not cita.ehr_id:
            # Generar un ID único de EHR usando el DNI del paciente
            ehr_id = f"EHR-{cita.paciente.dni}"  # El ID se genera con el DNI del paciente
            cita.ehr_id = ehr_id
            cita.estado = "confirmada"  # Cambiar el estado de la cita a confirmada

            cita.save()  # Guardamos los cambios
            print(f"Estado de la cita #{cita.id} actualizado a 'confirmada'. EHR ID: {ehr_id}")

            messages.success(
                request,
                f"Cita vinculada exitosamente con el registro EHR del paciente: {ehr_id}"
            )
        else:
            messages.info(request, f"La cita ya estaba vinculada con el ID EHR: {cita.ehr_id}")

    else:
        messages.info(request, "Esta cita ya ha sido atendida previamente.")

    # Mostrar resultado (confirmación)
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
    paciente = get_object_or_404(Entidad, id=paciente_id) # Verificar que el paciente exista
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
        dni = request.POST.get("dni") # Obtener el DNI ingresado


        if not doctor_id:
            errors["doctor_id"] = "Debe seleccionar un médico."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        if not dni:
            errors["dni"] = "Debe ingresar un DNI."

        if errors:
            return render(request, "citas/registrar_cita.html", {
                "especialidades": especialidades,
                "paciente": paciente,
                "doctores": doctores,
                "errors": errors,
                "selected_esp": especialidad_id,
                "selected_doc": selected_doc,
            })
        
        # Verificar si el paciente existe usando el DNI
        paciente = get_object_or_404(Entidad, dni=dni)  # Validación del DNI del paciente

        # doctor_id es DoctorDetalle.id
        doctor_detalle = get_object_or_404(DoctorDetalle, id=doctor_id)

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