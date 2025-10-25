from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from database.models import Cita, WaitlistItem, CheckIn

def hay_cupo_en_slot(doctor_horario) -> bool:
    # Hay cupo si NO existe una cita activa en ese slot
    return not Cita.objects.filter(doctor_horario=doctor_horario, estado__in=['pendiente', 'confirmada']).exists()

@transaction.atomic
def reservar_o_waitlist(paciente, doctor_horario) -> Cita | WaitlistItem:
    """
    Si hay cupo crea Cita(pendiente). Si no, añade a Waitlist.
    """
    if hay_cupo_en_slot(doctor_horario):
        return Cita.objects.create(paciente=paciente, doctor_horario=doctor_horario, estado='pendiente')
    else:
        item, created = WaitlistItem.objects.get_or_create(
        paciente=paciente, doctor_horario=doctor_horario,
        defaults={'estado': 'pendiente'}
        )
        return item

@transaction.atomic
def cancelar_y_ofertar(cita: Cita) -> WaitlistItem | None:
    """
    Cancela una cita y ofrece el cupo al primero de la lista de espera.
    """
    cita.estado = 'cancelada'
    cita.save(update_fields=['estado'])

    next_wait = WaitlistItem.objects.filter(
    doctor_horario=cita.doctor_horario, estado='pendiente'
    ).order_by('fecha_solicitud').first()

    if next_wait:
        # Marcar notificado (se debe enviar mensaje fuera de la transacción)
        next_wait.estado = 'notificado'
        next_wait.save(update_fields=['estado'])
        return next_wait
    return None

@transaction.atomic
def aceptar_oferta_waitlist(wait_item: WaitlistItem) -> Cita:
    """Convierte el cupo en una Cita pendiente y marca el ítem como aceptado."""
    if not hay_cupo_en_slot(wait_item.doctor_horario):
        raise ValueError('El cupo ya no está disponible')
    cita = Cita.objects.create(
        paciente=wait_item.paciente,
        doctor_horario=wait_item.doctor_horario,
        estado='pendiente'
    )
    wait_item.estado = 'aceptado'
    wait_item.save(update_fields=['estado'])
    return cita

@transaction.atomic
def registrar_checkin(cita: Cita) -> CheckIn:
    """Coloca al paciente en la cola de llegada y confirma la cita si estaba pendiente."""
    checkin, created = CheckIn.objects.get_or_create(cita=cita, defaults={'estado': 'en_espera'})
    if cita.estado == 'pendiente':
        cita.estado = 'confirmada'
        cita.save(update_fields=['estado'])
    return checkin

@transaction.atomic
def tomar_siguiente_para_atender(doctor) -> CheckIn | None:
    """
    Toma el siguiente check-in para un doctor (por sus slots actuales).
    Orden: hora_llegada ASC, pero puedes priorizar por hora de cita.
    """
    qs = CheckIn.objects.select_related('cita', 'cita__doctor_horario') \
        .filter(cita__doctor_horario__doctor=doctor, estado='en_espera') \
        .order_by('hora_llegada')

    nxt = qs.first()
    if nxt:
        nxt.estado = 'atendiendo'
        nxt.save(update_fields=['estado'])
    return nxt

@transaction.atomic
def finalizar_atencion(checkin: CheckIn):
    checkin.estado = 'atendido'
    checkin.save(update_fields=['estado'])

@transaction.atomic
def marcar_no_show_si_corresponde(cita: Cita, umbral_min=15) -> bool:
    """Marca no_show si pasó la hora de cita + umbral y no hay check-in."""
    hora_cita = cita.doctor_horario.horario.hora_inicio # Ajusta según tu modelo real
    if timezone.now() >= (hora_cita + timedelta(minutes=umbral_min)):
        if not hasattr(cita, 'checkin'):
            # No se presentó
            Cita.objects.filter(pk=cita.pk).update(estado='cancelada')
            return True
    return False