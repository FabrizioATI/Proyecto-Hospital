from django.utils import timezone
from datetime import datetime, timedelta
from database.models import Cita
from .sms_service import enviar_sms_recordatorio
from database.models import SMSNotification
from .sms_service import enviar_sms_from_notification


def procesar_recordatorios():
    """
    RF10 – Envía recordatorios 48h y 2h antes de la cita.
    Se ejecuta cada 10 minutos vía cron.
    """
    ahora = timezone.now()

    citas = Cita.objects.filter(
        estado="confirmada",
        doctor_horario__horario__fecha__gte=ahora.date()
    ).select_related("doctor_horario")

    for cita in citas:
        fecha_cita = timezone.make_aware(
            datetime.combine(
                cita.doctor_horario.horario.fecha,
                cita.doctor_horario.horario.hora_inicio
            )
        )

        # ---- Recordatorio 48 horas ----
        if fecha_cita - ahora <= timedelta(hours=48) and not cita.recordatorio_48h_enviado:
            enviar_sms_recordatorio(cita, tipo="recordatorio")
            cita.recordatorio_48h_enviado = True
            cita.save()

        # ---- Recordatorio 2 horas ----
        if fecha_cita - ahora <= timedelta(hours=2) and not cita.recordatorio_2h_enviado:
            enviar_sms_recordatorio(cita, tipo="recordatorio")
            cita.recordatorio_2h_enviado = True
            cita.save()

    # ------------------------------------------------
    # RF16 — Procesar encuestas programadas (tipo='encuesta')
    # ------------------------------------------------
    encuestas = SMSNotification.objects.filter(
        tipo='encuesta',
        estado='pendiente',
        fecha_envio__lte=ahora,
    ).select_related('cita', 'paciente')

    for encuesta in encuestas:
        try:
            enviar_sms_from_notification(encuesta)
        except Exception:
            # No queremos que un fallo crashee el cron; se registrará internamente
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error enviando encuesta SMS id=%s", encuesta.id)
