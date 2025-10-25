from django.db import transaction, IntegrityError
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import render, redirect, get_object_or_404
from database.models import Entidad, Especialidad, DoctorDetalle, DoctorHorario, Cita, DoctorDetalle, WaitlistItem, CheckIn
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from . import services
from .notifier import send_waitlist_offer_test
from django.utils.safestring import mark_safe

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
            try:
                with transaction.atomic():
                    # ¿El slot ya está ocupado por una cita activa?
                    ocupado = Cita.objects.filter(
                        doctor_horario_id=doctor_horario_id,
                        estado__in=["pendiente", "confirmada"],
                    ).exists()

                    doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)

                    if ocupado:
                        # 👉 En vez de error, envia a LISTA DE ESPERA
                        wait_item, _created = WaitlistItem.objects.get_or_create(
                            paciente=paciente,
                            doctor_horario=doctor_horario,
                            defaults={"estado": "pendiente"},
                        )
                        messages.info(
                            request,
                            "No hay cupo en ese horario. Te añadimos a la lista de espera."
                        )
                        return redirect("lista_citas_paciente", paciente_id=paciente_id)
                    else:
                        # Hay cupo: crea la cita pendiente
                        Cita.objects.create(
                            paciente=paciente,
                            doctor_horario=doctor_horario,
                            motivo=motivo,
                            estado="pendiente",
                        )
                        messages.success(request, "Cita registrada.")
                        return redirect("lista_citas_paciente", paciente_id=paciente_id)

            except IntegrityError:
                # Carrera: dos formularios al mismo tiempo. Fallback a waitlist.
                try:
                    doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
                    WaitlistItem.objects.get_or_create(
                        paciente=paciente,
                        doctor_horario=doctor_horario,
                        defaults={"estado": "pendiente"},
                    )
                    messages.info(
                        request,
                        "Ese horario se tomó al mismo tiempo. Te añadimos a la lista de espera."
                    )
                    return redirect("lista_citas_paciente", paciente_id=paciente_id)
                except Exception:
                    errors["doctor_horario"] = "Ese horario ya fue tomado por otro paciente."

    # GET: filtros y armado de combos
    especialidades = Especialidad.objects.all()

    doctores = (
        DoctorDetalle.objects.filter(especialidad_id=especialidad_id)
        if especialidad_id else []
    )

    # Anotar si el horario está ocupado para deshabilitarlo en el select
    horarios = []
    if doctor_id:
        horarios = (
            DoctorHorario.objects
            .filter(doctor_id=doctor_id)
            .select_related("horario")
            .annotate(
                ocupado=Exists(
                    Cita.objects.filter(
                        doctor_horario=OuterRef("pk"),
                        estado__in=["pendiente", "confirmada"]
                    )
                )
            )
        )

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
    services.registrar_checkin(cita)
    return render(request, 'citas/checkin_exitoso.html', {'cita': cita})

def cancelar_cita_view(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    next_wait = services.cancelar_y_ofertar(cita)
    if next_wait:
        accept_url = request.build_absolute_uri(
            reverse('aceptar_waitlist', args=[next_wait.id])
        )
        wa_url = send_waitlist_offer_test(next_wait, accept_url)
        messages.info(
            request,
            mark_safe(
                'Se ha ofrecido el cupo al siguiente en lista de espera. '
                f'<a class="btn btn-sm btn-success ms-2" href="{wa_url}" target="_blank" rel="noopener">Enviar WhatsApp de prueba</a>'
            )
        )
    else:
        messages.info(request, 'Cita cancelada y sin lista de espera pendiente.')
    return redirect('lista_citas_paciente', paciente_id=cita.paciente.id)

def aceptar_waitlist_view(request, item_id):
    item = get_object_or_404(WaitlistItem, pk=item_id)
    try:
        cita = services.aceptar_oferta_waitlist(item)
        messages.success(request, 'Has aceptado el cupo. Cita creada.')
        return redirect(reverse('citas:checkin', args=[cita.id]))
    except Exception as e:
        messages.error(request, f'No se pudo aceptar el cupo: {e}')
        return redirect('/')

def tablero_cola(request, doctor_id):
    doctor = get_object_or_404(DoctorDetalle, pk=doctor_id)
    en_espera = CheckIn.objects.select_related('cita', 'cita__paciente', 'cita__doctor_horario') \
        .filter(cita__doctor_horario__doctor=doctor, estado='en_espera') \
        .order_by('hora_llegada')
    atendiendo = CheckIn.objects.select_related('cita').filter(cita__doctor_horario__doctor=doctor, estado='atendiendo')
    atendidos = CheckIn.objects.select_related('cita').filter(cita__doctor_horario__doctor=doctor, estado='atendido').order_by('-hora_llegada')[:10]


    return render(request, 'citas/tablero_cola.html', {
        'doctor': doctor,
        'en_espera': en_espera,
        'atendiendo': atendiendo,
        'atendidos': atendidos,
    })
    
signer = TimestampSigner(salt="waitlist-offer")

def aceptar_waitlist_token_view(request, item_id, token):
    # Validar token (expira según tu TTL)
    try:
        # reconstruir la firma completa: "<id>:<firma>"
        signed_value = f"{item_id}:{token}"
        unsigned = signer.unsign(signed_value, max_age=60*60)  # 60 min de validez por ejemplo
        # opcional: también puedes verificar notificación vs TTL propio del item
    except (BadSignature, SignatureExpired):
        messages.error(request, "El enlace no es válido o ha expirado.")
        return redirect('/')

    wait_item = get_object_or_404(WaitlistItem, pk=item_id)

    # (opcional) valida expire por TTL del item si tienes notificado_at
    # if wait_item.notificado_at and timezone.now() > wait_item.notificado_at + timedelta(minutes=wait_item.ttl_respuesta_min):
    #     messages.error(request, "El tiempo de respuesta expiró.")
    #     return redirect('/')

    try:
        cita = services.aceptar_oferta_waitlist(wait_item)
        messages.success(request, "Has aceptado el cupo. Cita creada.")
        return redirect('citas:checkin', cita_id=cita.id)
    except Exception as e:
        messages.error(request, f"No se pudo aceptar el cupo: {e}")
        return redirect('/')