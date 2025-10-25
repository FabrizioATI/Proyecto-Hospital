from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from database.models import Cita
from .models import WaitlistItem
from .services import marcar_no_show_si_corresponde


@shared_task
def enviar_recordatorios():
    """Ejecutar cada 5 min: buscar citas a T-24h/T-3h/T-30min y enviar notificaciones."""
    pass

@shared_task
def expirar_waitlist():
    """Marcar waitlist notificado->expirado si supera TTL sin respuesta."""
    pass

@shared_task
def no_show_scheduler():
    """Marcar no-show de citas vencidas sin check-in y ofrecer cupo si aplica."""
    pass