"""
Servicio de notificaciones SMS con Twilio (RF12).
Encargado de enviar recordatorios, instrucciones y llamados de ingreso.
"""

from django.conf import settings
from django.utils import timezone
from database.models import SMSNotification, Cita
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
import logging

logger = logging.getLogger(__name__)


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


def enviar_sms_recordatorio(cita: Cita, tipo: str = 'recordatorio') -> bool:
    """
    Envía un SMS de recordatorio a un paciente con cita confirmada.
    
    Args:
        cita: Objeto Cita con estado confirmado
        tipo: Tipo de notificación ('recordatorio', 'instrucciones', 'llamado')
    
    Returns:
        bool: True si se envió exitosamente, False en caso contrario
    
    RF12: Registra el intento y estado de entrega
    """
    
    # Validaciones
    if not cita or cita.estado != 'confirmada':
        logger.warning(f"Cita #{cita.id if cita else 'None'} no está confirmada")
        return False
    
    paciente = cita.paciente
    if not paciente.telefono:
        logger.warning(f"Paciente {paciente.nombre_completo()} sin teléfono")
        return False
    
    # Obtener cliente Twilio
    client = obtener_cliente_twilio()
    if not client:
        logger.error("No se pudo obtener cliente de Twilio")
        return False
    
    # Construir mensaje según tipo
    mensaje = construir_mensaje_sms(cita, tipo)
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
        estado='enviado',
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
        # Registrar error de Twilio (RF12: registrar fallida)
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


def construir_mensaje_sms(cita: Cita, tipo: str) -> str:
    """
    Construye el mensaje SMS según el tipo de notificación.
    
    Args:
        cita: Objeto Cita
        tipo: 'recordatorio', 'instrucciones' o 'llamado'
    
    Returns:
        str: Mensaje formateado
    """
    
    paciente = cita.paciente
    doctor = cita.doctor
    horario = cita.doctor_horario.horario
    especialidad = cita.doctor_horario.doctor.especialidad
    
    fecha_str = horario.fecha.strftime('%d/%m/%Y')
    hora_str = horario.hora_inicio.strftime('%H:%M')
    
    if tipo == 'recordatorio':
        return (
            f"Hola {paciente.nombre}, le recordamos su cita con el "
            f"Dr. {doctor.apellidoPaterno} ({especialidad.nombre}) "
            f"el {fecha_str} a las {hora_str}. ¡No olvide asistir!"
        )
    
    elif tipo == 'instrucciones':
        return (
            f"Su cita es el {fecha_str} a las {hora_str} con "
            f"el Dr. {doctor.apellidoPaterno}. Por favor, llegar 10 minutos antes. "
            f"Tipo: {cita.tipo_cita}."
        )
    
    elif tipo == 'llamado':
        return (
            f"{paciente.nombre}, se le convoca a ingresar ahora para su "
            f"consulta con el Dr. {doctor.apellidoPaterno}. Presente en recepción."
        )
    
    else:
        return f"Recordatorio de cita para {paciente.nombre}"


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
