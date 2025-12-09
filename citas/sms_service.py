"""
Servicio de notificaciones SMS con Twilio (RF12).
Encargado de enviar recordatorios, instrucciones y llamados de ingreso.
"""

from django.conf import settings
from django.utils import timezone
from database.models import SMSNotification, Cita, NotificationPreference
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Cliente Twilio
# ============================================================

def obtener_cliente_twilio():
    """
    Obtiene el cliente de Twilio usando credenciales de settings.
    """
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    
    if not account_sid or not auth_token:
        logger.error("Credenciales de Twilio no configuradas en settings")
        return None
    
    return Client(account_sid, auth_token)


# ============================================================
# Envío de SMS
# ============================================================

def enviar_sms_recordatorio(cita: Cita, tipo: str = 'recordatorio') -> bool:
    """
    Envía un SMS de notificación a un paciente con cita (recordatorio, instrucciones, llamado).

    Args:
        cita: Objeto Cita
        tipo: Tipo de notificación ('recordatorio', 'instrucciones', 'llamado')
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    
    RF12: Registra el intento y estado de entrega
    """
    
    # Validaciones básicas de la cita
    if not cita or cita.estado != 'confirmada':  # ajusta este estado a tu flujo real
        logger.warning(f"Cita #{cita.id if cita else 'None'} no está confirmada")
        return False
    
    paciente = cita.paciente
    if not paciente.telefono:
        logger.warning(f"Paciente {paciente.nombre_completo()} sin teléfono")
        return False

    # Preferencias de notificación (consentimiento + idioma)
    notif_pref = getattr(paciente, "notif_pref", None)

    # Si no tiene preferencias o no dio consentimiento → NO se envía SMS
    if not notif_pref or not notif_pref.sms_consent:
        logger.info(
            f"Paciente {paciente.nombre_completo()} no tiene consentimiento SMS; "
            f"no se envía notificación."
        )
        return False

    # Idioma preferido, por defecto español
    lang = notif_pref.sms_language or "es"
    
    # Obtener cliente Twilio
    client = obtener_cliente_twilio()
    if not client:
        logger.error("No se pudo obtener cliente de Twilio")
        return False
    
    # Construir mensaje según tipo + idioma
    mensaje = construir_mensaje_sms(cita, tipo, lang=lang)
    if not mensaje:
        logger.error(f"No se pudo construir mensaje para tipo: {tipo}")
        return False
    
    # Obtener número de Twilio configurado
    twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    if not twilio_number:
        logger.error("TWILIO_PHONE_NUMBER no configurado en settings")
        return False
    
    # Crear registro de notificación (RF12: registrar intento)
    sms_notification = SMSNotification.objects.create(
        cita=cita,
        paciente=paciente,
        telefono=paciente.telefono,
        tipo=tipo,
        mensaje=mensaje,
        estado='enviado',  # se actualizará según respuesta
        intento=1,
    )
    
    try:
        # Enviar SMS con Twilio
        message = client.messages.create(
            body=mensaje,
            from_=twilio_number,
            to=paciente.telefono,
        )
        
        # Registrar respuesta exitosa (RF12: estado de entrega)
        sms_notification.sid = message.sid
        sms_notification.fecha_envio = timezone.now()
        sms_notification.respuesta_twilio = json.dumps({
            'sid': message.sid,
            'status': message.status,
            'error_code': message.error_code,
        })
        
        # Actualizar estado según respuesta
        if message.status in ['queued', 'sending', 'sent']:
            sms_notification.estado = 'enviado'
        elif message.status == 'delivered':
            sms_notification.estado = 'entregado'
            sms_notification.fecha_entrega = timezone.now()
        else:
            sms_notification.estado = 'fallido'
        
        sms_notification.save()
        
        logger.info(
            f"SMS enviado a {paciente.nombre_completo()} "
            f"({paciente.telefono}) - SID: {message.sid}"
        )
        
        return True
        
    except TwilioRestException as e:
        # Registrar error de Twilio (RF12: registrar fallo)
        sms_notification.estado = 'fallido'
        sms_notification.fecha_envio = timezone.now()
        sms_notification.respuesta_twilio = json.dumps({
            'error': str(e),
            'error_code': e.code,
        })
        sms_notification.save()
        
        logger.error(
            f"Error Twilio al enviar SMS a {paciente.nombre_completo()}: {e}"
        )
        
        return False
        
    except Exception as e:
        # Registrar error general
        sms_notification.estado = 'fallido'
        sms_notification.fecha_envio = timezone.now()
        sms_notification.respuesta_twilio = json.dumps({
            'error': str(e),
            'type': type(e).__name__,
        })
        sms_notification.save()
        
        logger.error(
            f"Error inesperado al enviar SMS a {paciente.nombre_completo()}: {e}"
        )
        
        return False


# ============================================================
# Construcción del mensaje (multilenguaje)
# ============================================================

def construir_mensaje_sms(cita: Cita, tipo: str, lang: str = "es") -> str:
    """
    Construye el mensaje SMS según el tipo de notificación y el idioma.
    
    Args:
        cita: Objeto Cita
        tipo: 'recordatorio', 'instrucciones' o 'llamado'
        lang: 'es' (español) o 'qu' (quechua)
    
    Returns:
        str: Mensaje formateado
    """
    
    paciente = cita.paciente
    doctor = cita.doctor
    horario = cita.doctor_horario.horario
    especialidad = cita.doctor_horario.doctor.especialidad
    
    fecha_str = horario.fecha.strftime('%d/%m/%Y')
    hora_str = horario.hora_inicio.strftime('%H:%M')

    # ==========================
    # Mensajes en ESPAÑOL
    # ==========================
    if lang == "es":
        if tipo == 'recordatorio':
            return (
                f"Hola {paciente.nombre}, le recordamos su cita con el "
                f"Dr. {doctor.apellidoPaterno} ({especialidad.nombre}) "
                f"el {fecha_str} a las {hora_str}. ¡No olvide asistir!"
            )
        
        elif tipo == 'instrucciones':
            return (
                f"Su cita es el {fecha_str} a las {hora_str} con "
                f"el Dr. {doctor.apellidoPaterno}. Por favor, llegue 10 minutos antes. "
                f"Tipo: {cita.tipo_cita}."
            )
        
        elif tipo == 'llamado':
            return (
                f"{paciente.nombre}, se le convoca a ingresar ahora para su "
                f"consulta con el Dr. {doctor.apellidoPaterno}. Preséntese en recepción."
            )

    # ==========================
    # Mensajes en QUECHUA
    # (puedes afinar estos textos con un traductor humano)
    # ==========================
    if lang == "qu":
        if tipo == 'recordatorio':
            return (
                f"Rimaykullayki {paciente.nombre}, hampikuykita "
                f"Dr. {doctor.apellidoPaterno} ({especialidad.nombre}) "
                f"wan {fecha_str} {hora_str}-ta yuyarinaykuy."
            )
        
        elif tipo == 'instrucciones':
            return (
                f"Hampikuykita {fecha_str} {hora_str}-ta kanki "
                f"Dr. {doctor.apellidoPaterno} wan. "
                f"10 minutos ñawpaqta hamuy. Tipo: {cita.tipo_cita}."
            )
        
        elif tipo == 'llamado':
            return (
                f"{paciente.nombre}, kunan hamuy hampikuykipaq "
                f"Dr. {doctor.apellidoPaterno} wan. "
                f"Recepciónman rinaykuy."
            )

    # Fallback genérico
    return f"Recordatorio de cita para {paciente.nombre}"


# ============================================================
# Reintento de SMS fallidos
# ============================================================

def reintentar_sms_fallido(sms_notification: SMSNotification, max_intentos: int = 3) -> bool:
    """
    Reintenta enviar un SMS que falló anteriormente.
    
    Args:
        sms_notification: Registro SMSNotification fallido
        max_intentos: Máximo número de intentos
    
    Returns:
        bool: True si se reintentó exitosamente
    """
    
    if sms_notification.intento >= max_intentos:
        logger.warning(
            f"SMS #{sms_notification.id} superó máximo de intentos "
            f"({max_intentos})"
        )
        return False
    
    if sms_notification.estado != 'fallido':
        logger.warning(
            f"SMS #{sms_notification.id} no está en estado 'fallido' "
            f"(estado actual: {sms_notification.estado})"
        )
        return False
    
    # Respetar nuevamente el consentimiento por si cambió
    paciente = sms_notification.paciente
    notif_pref = getattr(paciente, "notif_pref", None)
    if not notif_pref or not notif_pref.sms_consent:
        logger.info(
            f"Paciente {paciente.nombre_completo()} retiró su consentimiento SMS; "
            f"no se reintenta envío."
        )
        return False

    client = obtener_cliente_twilio()
    if not client:
        return False
    
    twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    if not twilio_number:
        return False
    
    try:
        message = client.messages.create(
            body=sms_notification.mensaje,
            from_=twilio_number,
            to=sms_notification.telefono,
        )
        
        sms_notification.intento += 1
        sms_notification.sid = message.sid
        sms_notification.fecha_envio = timezone.now()
        sms_notification.estado = 'enviado'
        sms_notification.respuesta_twilio = json.dumps({
            'sid': message.sid,
            'status': message.status,
        })
        sms_notification.save()
        
        logger.info(f"SMS #{sms_notification.id} reintentado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al reintentar SMS #{sms_notification.id}: {e}")
        return False


def construir_mensaje_encuesta(cita: Cita, lang: str = "es") -> str:
    """
    Construye un mensaje breve con el enlace a la encuesta de satisfacción (NPS).
    Usa la configuración `SURVEY_URL` en `settings.py`.
    """
    from django.conf import settings

    paciente = cita.paciente
    survey_url = getattr(settings, 'SURVEY_URL', 'https://forms.gle/XXXXXXXX')

    if lang == 'es':
        return f"Gracias por asistir a su cita, {paciente.nombre}. Por favor califique su experiencia: {survey_url}"
    if lang == 'qu':
        return f"Yuspagaraqmi tapuykita, {paciente.nombre}. Rikuykuy qampi: {survey_url}"

    return f"Por favor complete la encuesta: {survey_url}"


def enviar_sms_from_notification(sms_notification: SMSNotification) -> bool:
    """
    Envía un SMS usando los datos ya preparados en un registro `SMSNotification`.
    Actualiza el registro con SID/estado/respuesta.
    """
    # Validar consentimiento actualizado
    paciente = sms_notification.paciente
    notif_pref = getattr(paciente, 'notif_pref', None)
    if not notif_pref or not notif_pref.sms_consent:
        logger.info(f"Paciente {paciente.nombre_completo()} no tiene consentimiento; no se envía encuesta.")
        sms_notification.estado = 'fallido'
        sms_notification.respuesta_twilio = json.dumps({'error': 'no_consent'})
        sms_notification.save()
        return False

    client = obtener_cliente_twilio()
    if not client:
        logger.error("No se pudo obtener cliente Twilio para enviar encuesta")
        return False

    twilio_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    if not twilio_number:
        logger.error("TWILIO_PHONE_NUMBER no configurado en settings")
        return False

    try:
        message = client.messages.create(
            body=sms_notification.mensaje,
            from_=twilio_number,
            to=sms_notification.telefono,
        )

        sms_notification.sid = message.sid
        sms_notification.fecha_envio = timezone.now()
        sms_notification.respuesta_twilio = json.dumps({
            'sid': message.sid,
            'status': message.status,
            'error_code': message.error_code,
        })

        if message.status in ['queued', 'sending', 'sent']:
            sms_notification.estado = 'enviado'
        elif message.status == 'delivered':
            sms_notification.estado = 'entregado'
            sms_notification.fecha_entrega = timezone.now()
        else:
            sms_notification.estado = 'fallido'

        sms_notification.save()
        logger.info(f"Encuesta SMS enviada (SMS #{sms_notification.id}) a {paciente.nombre_completo()}")
        return True

    except Exception as e:
        sms_notification.estado = 'fallido'
        sms_notification.fecha_envio = timezone.now()
        sms_notification.respuesta_twilio = json.dumps({'error': str(e), 'type': type(e).__name__})
        sms_notification.save()
        logger.error(f"Error al enviar encuesta SMS #{sms_notification.id}: {e}")
        return False


# ============================================================
# Consulta de estado en Twilio
# ============================================================

def obtener_estado_entrega_sms(sid: str) -> str:
    """
    Consulta a Twilio el estado de entrega de un SMS usando su SID.
    
    Args:
        sid: SID de Twilio del mensaje
    
    Returns:
        str: Estado del mensaje ('queued', 'sending', 'sent', 'delivered', 'failed', etc.)
    """
    
    client = obtener_cliente_twilio()
    if not client:
        return 'unknown'
    
    try:
        message = client.messages(sid).fetch()
        return message.status
    except Exception as e:
        logger.error(f"Error al consultar estado del SMS {sid}: {e}")
        return 'unknown'
