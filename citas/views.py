
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
    DoctorHorario, Cita, WaitlistItem, HistoriaClinica, EpisodioClinico, Derivacion
)
from django.db.models import Q
from django.db.models import Count, Max
from functools import wraps
from django.utils import timezone
from datetime import timedelta

#Index
def index(request):
    return render(request, "home/index.html")

# CRUD de Citas
from django.http import HttpResponseForbidden
from database.models import Cita

def lista_citas_paciente(request, paciente_id):
    es_admin = request.session.get("codigo_rol") == "003"

    # Evita que un paciente vea citas de otro paciente
    if not es_admin:
        if request.session.get("entidad_id") != int(paciente_id):
            return HttpResponseForbidden("No autorizado")

    # Admin ve todo; paciente solo las suyas
    if es_admin:
        citas = (Cita.objects
                 .select_related("paciente",
                                 "doctor_horario__doctor__entidad",
                                 "doctor_horario__horario")
                 .order_by("-fecha_creacion"))
    else:
        citas = (Cita.objects
                 .select_related("paciente",
                                 "doctor_horario__doctor__entidad",
                                 "doctor_horario__horario")
                 .filter(paciente_id=paciente_id)
                 .order_by("-fecha_creacion"))

    # Si tu template usa lógica por rol, envíale el tipo de usuario
    tipo_usuario = "admin" if es_admin else "paciente"

    return render(request, "citas/lista_citas.html", {
        "citas": citas,
        "tipo_usuario": tipo_usuario,   # útil para ocultar/mostrar acciones
    })

def editar_cita_paciente(request, paciente_id, pk):
    es_admin = request.session.get("codigo_rol") == "003"

    # Seguridad: un paciente no puede editar citas de otro paciente
    if not es_admin and request.session.get("entidad_id") != int(paciente_id):
        return HttpResponseForbidden("No autorizado")

    # Admin puede cargar por PK; paciente debe coincidir el paciente_id
    if es_admin:
        cita = get_object_or_404(Cita, pk=pk)
    else:
        cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)

    errors = {}
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(
        especialidad=cita.doctor_horario.doctor.especialidad
    )
    horarios = DoctorHorario.objects.filter(
        doctor=cita.doctor_horario.doctor
    ).select_related("horario")

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        tipo_cita = request.POST.get("tipo_cita")

        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        if tipo_cita not in ["PRESENCIAL", "VIRTUAL"]:
            errors["tipo_cita"] = "Debe seleccionar una modalidad válida."

        if not errors:
            cita.motivo = motivo
            cita.tipo_cita = tipo_cita
            cita.save()
            messages.success(request, "La cita se actualizó correctamente.")
            # Redirige a la lista del paciente dueño de la cita (sirve para admin y paciente)
            return redirect("lista_citas_paciente", paciente_id=cita.paciente_id)

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

    if cita.estado == "ATENDIDA":
        messages.info(request, "Esta cita ya ha sido atendida previamente.")
        return render(request, 'citas/checkin_exitoso.html', {'cita': cita})

    services.registrar_checkin(cita)

    historia, _ = HistoriaClinica.objects.get_or_create(paciente=cita.paciente)

    episodio, created_ep = EpisodioClinico.objects.get_or_create(
        historia=historia,
        cita=cita,
        defaults={'tipo': 'consulta', 'motivo': cita.motivo or ''}
    )

    if cita.estado.lower() not in ("confirmada", "atendiendo", "atendida"):
        cita.estado = "confirmada"
        cita.save(update_fields=["estado"])

    if created_ep:
        messages.success(
            request,
            f"Cita vinculada a la Historia Clínica {historia.numero}. Episodio #{episodio.id} creado."
        )
    else:
        messages.info(
            request,
            f"La cita ya estaba vinculada al Episodio #{episodio.id} de la Historia {historia.numero}."
        )

    return render(request, 'citas/checkin_exitoso.html', {'cita': cita})

def cancelar_cita_view(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    # --- quién eres ---
    rol = request.session.get("codigo_rol")     # "001" doctor, "002" paciente, "003" admin
    usuario_id = request.session.get("entidad_id")

    # --- regla de autorización ---
    es_duenio_paciente = (rol == "002" and cita.paciente_id == usuario_id)
    es_duenio_doctor   = (rol == "001" and cita.doctor_horario.doctor.entidad_id == usuario_id)
    es_admin           = (rol == "003")

    if not (es_duenio_paciente or es_duenio_doctor or es_admin):
        messages.error(request, "No estás autorizado para cancelar esta cita.")
        # redirige a una vista coherente según el rol
        if rol == "001":
            return redirect("lista_citas_doctor", doctor_id=usuario_id)
        elif rol == "002":
            return redirect("lista_citas_paciente", paciente_id=usuario_id)
        return redirect("index")

    # --- validación de estado ---
    if cita.estado in ("CANCELADA", "ATENDIDA"):
        messages.info(request, f"La cita ya está en estado {cita.estado}.")
    else:
        # tu service hace el trabajo (cancelar y ofertar al siguiente de la waitlist)
        services.cancelar_y_ofertar(cita)
        messages.success(request, "Cita cancelada correctamente.")

    # --- siempre devolver una respuesta ---
    if rol == "001":
        return redirect("lista_citas_doctor", doctor_id=usuario_id)
    else:
        # para admin y paciente mostramos la lista del paciente de la cita
        return redirect("lista_citas_paciente", paciente_id=cita.paciente_id)

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
    """
    - Mantiene selección de paciente (solo admin) al cambiar especialidad/doctor (GET).
    - En POST respeta reglas de clasificación por rol.
    - Valida límite de 2 citas activas por especialidad.
    """
    # Valida que la ruta tenga un paciente válido (no necesariamente el elegido)
    paciente_url = get_object_or_404(Entidad, id=paciente_id)
    errors = {}

    # --- Rol ---
    es_admin = request.session.get("codigo_rol") == "003"

    # --- GET: filtros/combos ---
    especialidades = Especialidad.objects.all()
    especialidad_id = request.GET.get("especialidad")
    selected_doc = request.GET.get("doctor")

    # Mantener selección de paciente en cada GET (para admin)
    selected_paciente_id = request.GET.get("paciente_sel") if es_admin else None

    doctores = get_doctores_con_horario(especialidad_id) if especialidad_id else []

    # Lista de pacientes SOLO para admin
    pacientes_list = []
    if es_admin:
        pacientes_list = (
            Entidad.objects
            .filter(rolentidad__rol__codigo_rol="002")  # 002 = Paciente
            .order_by("apellidoPaterno", "apellidoMaterno", "nombre")
            .distinct()
        )

    # --- POST: crear solicitud ---
    if request.method == "POST":
        doctor_id    = request.POST.get("doctor_id")       # DoctorDetalle.id
        clasificacion = request.POST.get("clasificacion") or "REGULAR"
        tipo_cita     = request.POST.get("tipo_cita") or "PRESENCIAL"
        motivo        = request.POST.get("motivo")
        dni           = request.POST.get("dni")

        # si viene hidden desde el template, úsalo
        paciente_sel = request.POST.get("paciente_sel") or selected_paciente_id

        # Clasificaciones permitidas por rol
        allowed = {"EMERGENCIA", "ADULTO_MAYOR", "REGULAR"} if es_admin else {"ADULTO_MAYOR", "REGULAR"}
        if clasificacion not in allowed:
            errors["clasificacion"] = "No estás autorizado para usar esta clasificación."

        # Validaciones básicas
        if not doctor_id:
            errors["doctor_id"] = "Debe seleccionar un médico."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        # Resolver paciente según rol
        paciente_obj = None
        if es_admin:
            if paciente_sel:
                paciente_obj = get_object_or_404(Entidad, id=paciente_sel)
            elif dni:
                paciente_obj = get_object_or_404(Entidad, dni=dni)
            else:
                errors["dni"] = "Seleccione un paciente o ingrese DNI."
        else:
            if not dni:
                errors["dni"] = "Debe ingresar un DNI."
            else:
                paciente_obj = get_object_or_404(Entidad, dni=dni)

        if errors:
            return render(request, "citas/registrar_cita.html", {
                "especialidades": especialidades,
                "paciente": paciente_url,
                "doctores": doctores,
                "errors": errors,
                "selected_esp": int(especialidad_id) if especialidad_id else None,
                "selected_doc": int(selected_doc) if selected_doc else None,
                "pacientes": pacientes_list,
                "es_admin": es_admin,
                "selected_paciente_id": paciente_sel,
            })

        # doctor_id es DoctorDetalle.id
        doctor_detalle = get_object_or_404(DoctorDetalle, id=doctor_id)

        # Obtener la especialidad
        especialidad = doctor_detalle.especialidad

        # ============================================================
        # 🔥 RF20: Validación de derivación si la especialidad la exige
        # ============================================================
        if especialidad.requiere_derivacion:
            tiene_derivacion = Derivacion.objects.filter(
                paciente=paciente_obj,
                especialidad=especialidad,
                valido=True
            ).exists()

            if not tiene_derivacion:
                messages.error(
                    request,
                    f"La especialidad {especialidad.nombre} requiere una derivación médica previa."
                )

                return render(request, "citas/registrar_cita.html", {
                    "especialidades": especialidades,
                    "paciente": paciente_url,
                    "doctores": doctores,
                    "errors": errors,
                    "selected_esp": int(especialidad_id) if especialidad_id else None,
                    "selected_doc": int(selected_doc) if selected_doc else None,
                    "pacientes": pacientes_list,
                    "es_admin": es_admin,
                    "selected_paciente_id": paciente_sel,

                    # Nuevo: bandera para UI
                    "requiere_derivacion": True,
                    "especialidad_bloqueada": especialidad.nombre,
                })
        # ============================================================

        # Límite: 2 citas activas por especialidad
        citas_activas = Cita.objects.filter(
            paciente=paciente_obj,
            doctor_horario__doctor__especialidad=especialidad,
            estado__in=["pendiente", "confirmada"]
        ).count()
        if citas_activas >= 2:
            messages.error(request, "Límite de citas activas alcanzado para esta especialidad")
            return redirect("lista_citas_paciente", paciente_id=paciente_obj.id)

        # --- Verificar cupos diarios / semanales del doctor ---
        cupos_diarios = doctor_detalle.cupos_diarios
        cupos_semanales = doctor_detalle.cupos_semanales

        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes
        fin_semana = inicio_semana + timedelta(days=6)

        citas_dia = Cita.objects.filter(
            doctor_horario__doctor=doctor_detalle,
            doctor_horario__horario__fecha=hoy,
            estado="EN_ESPERA",
        ).count()

        citas_semana = Cita.objects.filter(
            doctor_horario__doctor=doctor_detalle,
            doctor_horario__horario__fecha__gte=inicio_semana,
            doctor_horario__horario__fecha__lte=fin_semana,
            estado="EN_ESPERA",
        ).count()

        capacidad_diaria_agotada = (cupos_diarios is not None and citas_dia >= cupos_diarios)
        capacidad_semanal_agotada = (cupos_semanales is not None and citas_semana >= cupos_semanales)

        if capacidad_diaria_agotada or capacidad_semanal_agotada:
            aceptar_wait = request.POST.get("aceptar_waitlist")
            if not aceptar_wait:
                messages.warning(request, "Los cupos del doctor están agotados para la fecha/semana seleccionada.")
                return render(request, "citas/registrar_cita.html", {
                    "especialidades": especialidades,
                    "paciente": paciente_url,
                    "doctores": doctores,
                    "errors": errors,
                    "selected_esp": int(especialidad_id) if especialidad_id else None,
                    "selected_doc": int(selected_doc) if selected_doc else None,
                    "pacientes": pacientes_list,
                    "es_admin": es_admin,
                    "selected_paciente_id": paciente_sel,
                    "capacidad_agotada": True,
                    "capacidad_diaria_agotada": capacidad_diaria_agotada,
                    "capacidad_semanal_agotada": capacidad_semanal_agotada,
                    "citas_dia": citas_dia,
                    "citas_semana": citas_semana,
                    "cupos_diarios": cupos_diarios,
                    "cupos_semanales": cupos_semanales,
                })

        # Registrar solicitud
        solicitar_cita(
            paciente=paciente_obj,
            doctor_detalle=doctor_detalle,
            clasificacion=clasificacion,
            tipo_cita=tipo_cita,
            motivo=motivo,
        )

        messages.success(
            request,
            "Tu solicitud de cita ha sido registrada. "
            "El sistema asignará el horario automáticamente según tu prioridad."
        )
        return redirect("lista_citas_paciente", paciente_id=paciente_obj.id)

    # --- GET: render inicial ---
    return render(request, "citas/registrar_cita.html", {
        "especialidades": especialidades,
        "paciente": paciente_url,
        "doctores": doctores,
        "errors": errors,
        "selected_esp": int(especialidad_id) if especialidad_id else None,
        "selected_doc": int(selected_doc) if selected_doc else None,
        "pacientes": pacientes_list,
        "es_admin": es_admin,
        "selected_paciente_id": selected_paciente_id,
    })


def marcar_cita_atendida(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    # Solo doctor
    if request.session.get("codigo_rol") != "001":
        messages.error(request, "Solo un doctor puede marcar una cita como atendida.")
        return redirect('lista_citas_paciente', paciente_id=cita.paciente_id)

    # Debe ser el doctor dueño de la cita
    doctor_sesion_id = request.session.get("entidad_id")
    if cita.doctor_horario.doctor.entidad_id != doctor_sesion_id:
        messages.error(request, "No puedes marcar citas de otro doctor.")
        return redirect('lista_citas_doctor', doctor_id=doctor_sesion_id)

    if cita.estado == "ATENDIDA":
        messages.info(request, "La cita ya estaba atendida.")
    else:
        services.atender_y_asociar(cita)
        messages.success(request, "Cita marcada como ATENDIDA.")

    # Siempre responde con un redirect (HttpResponse)
    return redirect('lista_citas_doctor', doctor_id=doctor_sesion_id)

def lista_historias_clinicas(request):
    """Admin ve todas; Doctor ve solo historias de sus pacientes (con los que tuvo citas)."""
    rol = request.session.get("codigo_rol")
    if rol not in ("001", "003"):
        return render(request, "403.html", status=403)

    q = (request.GET.get("q") or "").strip()

    if rol == "003":  # Admin
        qs = (HistoriaClinica.objects
              .select_related("paciente")
              .annotate(
                  total_episodios=Count("episodios", distinct=True),
                  total_notas=Count("episodios__notas", distinct=True),
                  ultima_atencion=Max("episodios__inicio"),
              )
              .order_by("-ultima_atencion",
                        "paciente__apellidoPaterno",
                        "paciente__apellidoMaterno",
                        "paciente__nombre"))
    else:  # Doctor
        doctor_entidad_id = request.session.get("entidad_id")
        # Historias de pacientes que tengan al menos una cita con este doctor
        qs = (HistoriaClinica.objects
              .select_related("paciente")
              .filter(paciente__citas_paciente__doctor_id=doctor_entidad_id)
              .annotate(
                  total_episodios=Count("episodios", distinct=True),
                  total_notas=Count("episodios__notas", distinct=True),
                  ultima_atencion=Max("episodios__inicio"),
              )
              .distinct()
              .order_by("-ultima_atencion",
                        "paciente__apellidoPaterno",
                        "paciente__apellidoMaterno",
                        "paciente__nombre"))

    if q:
        qs = qs.filter(
            Q(paciente__dni__icontains=q) |
            Q(paciente__nombre__icontains=q) |
            Q(paciente__apellidoPaterno__icontains=q) |
            Q(paciente__apellidoMaterno__icontains=q) |
            Q(numero__icontains=q)
        )

    return render(request, "ehr/historias_list.html", {
        "historias": qs,
        "q": q,
    })

def detalle_historia_clinica(request, historia_id):
    """Admin puede ver cualquiera; Doctor solo si tuvo citas con ese paciente."""
    rol = request.session.get("codigo_rol")
    if rol not in ("001", "003"):
        return render(request, "403.html", status=403)

    historia = get_object_or_404(
        HistoriaClinica.objects.select_related("paciente"),
        pk=historia_id
    )

    if rol == "001":  # Doctor: valida vínculo con paciente por citas
        doctor_entidad_id = request.session.get("entidad_id")
        tiene_vinculo = Cita.objects.filter(
            paciente=historia.paciente,
            doctor_id=doctor_entidad_id
        ).exists()
        if not tiene_vinculo:
            return render(request, "403.html", status=403)

    episodios = (EpisodioClinico.objects
                 .filter(historia=historia)
                 .select_related("cita")
                 .annotate(total_notas=Count("notas"))
                 .order_by("-inicio"))

    return render(request, "ehr/historia_detalle.html", {
        "historia": historia,
        "episodios": episodios,
    })