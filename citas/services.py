from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from database.models import (
    Cita,
    WaitlistItem,
    DoctorDetalle,
    DoctorHorario,
)

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
    for idx, horario in enumerate(horarios):
        if idx >= len(items):
            break

        item = items[idx]
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