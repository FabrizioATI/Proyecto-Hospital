from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from database.models import (
    Cita,
    WaitlistItem,
    DoctorDetalle,
    DoctorHorario,
)
from .sms_service import enviar_sms_recordatorio
from database.models import SMSNotification
from django.conf import settings
from datetime import timedelta
from .sms_service import construir_mensaje_encuesta

PRIORIDAD_MAP = {
    'EMERGENCIA': 1,
    'ADULTO_MAYOR': 2,
    'REGULAR': 3,
}


def get_doctores_con_horario(especialidad_id):
    """
    Devuelve doctores de una especialidad que tengan horarios futuros configurados.
    """
    hoy = timezone.now().date()
    if not especialidad_id:
        return DoctorDetalle.objects.none()

    return (
        DoctorDetalle.objects
        .filter(
            especialidad_id=especialidad_id,
            doctorhorario__horario__fecha__gte=hoy,
        )
        .select_related("entidad", "especialidad")
        .distinct()
    )


def _get_prioridad_num(clasificacion):
    return PRIORIDAD_MAP.get(clasificacion, 3)


@transaction.atomic
def solicitar_cita(paciente, doctor_detalle, clasificacion, motivo, tipo_cita):
    """
    1. Registra la solicitud en la waitlist (sin horario).
    2. Lanza el motor de colas para ese doctor.
    """
    wait_item = WaitlistItem.objects.create(
        paciente=paciente,
        doctor_horario=None,
        motivo=motivo,
        tipo_cita=tipo_cita,
        clasificacion=clasificacion,
    )

    procesar_cola_doctor(doctor_detalle)

    return wait_item


@transaction.atomic
def procesar_cola_doctor(doctor_detalle: DoctorDetalle):
    """
    Reordena y reasigna TODOS los horarios del doctor según la cola y prioridad.
    Si entra una emergencia, se mueve al primer turno disponible.
    """

    hoy = timezone.now().date()

    # 1. Horarios futuros del doctor
    horarios = list(
        DoctorHorario.objects
        .select_related('horario')
        .filter(doctor=doctor_detalle, horario__fecha__gte=hoy)
        .order_by('horario__fecha', 'horario__hora_inicio')
    )

    if not horarios:
        return  # no hay horarios → todos quedan en waitlist sin horario

    # 2. Items de la waitlist relevantes (pendientes/aceptados)
    items = list(
        WaitlistItem.objects
        .select_related('paciente', 'doctor_horario')
        .filter(
            estado__in=['pendiente', 'aceptado'],
        )
        .order_by('fecha_solicitud')
    )

    # Orden por prioridad y luego por antigüedad
    items.sort(key=lambda i: (_get_prioridad_num(i.clasificacion), i.fecha_solicitud))

    # 3. Emparejar items con horarios
    # Se usa un índice separado porque algunos horarios pueden ser saltados
    # si la capacidad por hora de la especialidad ya está completa.
    item_idx = 0
    for horario in horarios:
        if item_idx >= len(items):
            break

        # Capacidad por hora por especialidad (ej: 10)
        especialidad = horario.doctor.especialidad
        fecha = horario.horario.fecha
        hora = horario.horario.hora_inicio

        current_count = Cita.objects.filter(
            doctor_horario__horario__fecha=fecha,
            doctor_horario__horario__hora_inicio=hora,
            doctor_horario__doctor__especialidad=especialidad,
            estado="EN_ESPERA",
        ).count()

        capacidad = getattr(especialidad, 'capacidad_por_hora', 10)
        if current_count >= capacidad:
            # La especialidad ya alcanzó el límite para este horario; no asignamos aquí
            continue

        item = items[item_idx]
        item.doctor_horario = horario
        item.estado = 'aceptado'
        item.save()

        Cita.objects.update_or_create(
            paciente=item.paciente,
            doctor_horario=horario,
            defaults={
                "doctor": doctor_detalle.entidad,
                "motivo": item.motivo,
                "clasificacion": item.clasificacion,
                "estado": "EN_ESPERA",
            }
        )

        item_idx += 1

    # 4. Resto se queda sin horario (cola pura)
    for item in items[len(horarios):]:
        # Si antes tenía un horario asignado, cancelamos esa cita
        if item.doctor_horario:
            Cita.objects.filter(
                paciente=item.paciente,
                doctor_horario=item.doctor_horario,
                estado="EN_ESPERA",   # solo las que aún no se atendieron
            ).update(estado="CANCELADA")

        # Lo devolvemos a la cola pura (sin horario)
        item.doctor_horario = None
        item.estado = 'pendiente'
        item.save()
        
@transaction.atomic
def cancelar_y_ofertar(cita: Cita):
    # 1) Cancelar la cita actual
    cita.estado = "CANCELADA"
    cita.save()

    horario_libre = cita.doctor_horario
    if not horario_libre:
        return None

    doctor_detalle = horario_libre.doctor

    qs = (
        WaitlistItem.objects
        .select_related("paciente", "doctor_horario")
        .filter(estado="pendiente")
        .filter(
            Q(doctor_horario__doctor=doctor_detalle) | Q(doctor_horario__isnull=True)
        )
    )
    if not qs.exists():
        return None

    candidatos = list(qs)
    candidatos.sort(key=lambda i: (_get_prioridad_num(i.clasificacion), i.fecha_solicitud))

    next_wait = candidatos[0]

    # Asignar horario y marcar como aceptado (si no quieres paso de confirmación)
    next_wait.doctor_horario = horario_libre
    next_wait.estado = "aceptado"   # o "notificado" si igual quieres confirmación
    next_wait.save()

    # 👉 Crear / actualizar la Cita para este paciente
    Cita.objects.update_or_create(
        paciente=next_wait.paciente,
        doctor_horario=horario_libre,
        defaults={
            "doctor": doctor_detalle.entidad,
            "motivo": next_wait.motivo,
            "clasificacion": next_wait.clasificacion,
            "estado": "EN_ESPERA",
        },
    )

    return next_wait

@transaction.atomic
def atender_y_asociar(cita):
    cita.estado = "ATENDIDA"
    cita.save()
    # Programar envío de encuesta NPS/satisfacción 2 horas después si el paciente dio consentimiento
    try:
        paciente = cita.paciente
        notif_pref = getattr(paciente, 'notif_pref', None)
        if notif_pref and notif_pref.sms_consent:
            fecha_envio = timezone.now() + timedelta(hours=2)
            # construir mensaje (usa link de encuesta configurable en settings)
            lang = notif_pref.sms_language or 'es'
            mensaje = construir_mensaje_encuesta(cita, lang=lang)

            SMSNotification.objects.create(
                cita=cita,
                paciente=paciente,
                telefono=paciente.telefono or '',
                tipo='encuesta',
                mensaje=mensaje,
                estado='pendiente',
                fecha_envio=fecha_envio,
            )
    except Exception:
        # No queremos bloquear el flujo por errores en la programación
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error programando encuesta para cita #%s", getattr(cita, 'id', '?'))

@transaction.atomic
def liberar_horario(doctor_horario: DoctorHorario):
    """
    Elimina un DoctorHorario de forma segura:
    - Citas EN_ESPERA con ese horario → CANCELADA
    - Items de waitlist vinculados a ese horario → vuelven a 'pendiente' sin horario
    - Borra el horario y la relación
    - Reprocesa la cola del doctor por si puede reasignar a otros horarios
    """
    doctor_detalle = doctor_horario.doctor
    horario = doctor_horario.horario

    # 1) Citas que usan este horario → CANCELADA (solo las aún no atendidas)
    Cita.objects.filter(
        doctor_horario=doctor_horario,
        estado="EN_ESPERA",
    ).update(estado="CANCELADA")

    # 2) Waitlist: volver a cola pura
    for item in WaitlistItem.objects.filter(doctor_horario=doctor_horario):
        item.doctor_horario = None
        item.estado = "pendiente"
        item.save()

    # 3) Eliminar horario y relación
    doctor_horario.delete()
    horario.delete()

    # 4) Reprocesar cola con los horarios restantes
    procesar_cola_doctor(doctor_detalle)

@transaction.atomic
def registrar_checkin(cita):
    """
    Registra el check-in de la cita. 
    Vincula la cita con un EHR ID y cambia el estado de la cita a "confirmada".
    Envía SMS de recordatorio al paciente (RF12).
    """
    # Verificar si ya tiene un EHR ID. Si no lo tiene, generarlo.
    if not cita.ehr_id:
        ehr_id = f"EHR-{cita.paciente.dni}"  # Usamos el DNI del paciente para generar un ID único
        cita.ehr_id = ehr_id
        cita.estado = "confirmada"  # Cambiar el estado de la cita a confirmada
        cita.save()
        
        # RF12: Enviar SMS de recordatorio cuando la cita se confirma
        try:
            enviar_sms_recordatorio(cita, tipo='recordatorio')
        except Exception as e:
            # Log del error pero no bloquea la confirmación de cita
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error al enviar SMS para cita #{cita.id}: {e}")
    else:
        # Si ya tiene un EHR ID, no hacemos nada
        pass