import smtplib
from email.mime.text import MIMEText


def send_waitlist_offer_email_test(wait_item, destinatario: str) -> str:
    """
    Envía un correo de prueba al paciente usando SMTP.
    - wait_item: objeto que contiene paciente y ttl_respuesta_min
    - destinatario: correo al que enviar el mensaje
    """

    # --- Datos del remitente ---
    remitente = "fabriziomendoza1005@gmail.com"
    password = ""  # tu app password de Gmail

    # --- Datos del paciente ---
    paciente = wait_item.paciente
    nombre = f"{paciente.nombre} {paciente.apellidoPaterno}".strip()

    # --- Armar mensaje ---
    cuerpo = (
        f"Hola {nombre}, se liberó un cupo.\n\n"
        f"Tienes {wait_item.ttl_respuesta_min} minutos para aceptarlo.\n"
        f"Este es un correo de PRUEBA enviado desde Python. 😊"
    )

    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = "Cupo disponible - Notificación"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    # --- Enviar ---
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remitente, password)
            smtp.send_message(mensaje)
        return "Correo enviado correctamente 🎉"

    except Exception as e:
        return f"Error al enviar correo: {e}"

