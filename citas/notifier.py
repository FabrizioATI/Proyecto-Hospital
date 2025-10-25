from pyexpat.errors import messages
from urllib.parse import quote_plus

def build_wa_click_to_chat(phone: str, text: str) -> str:
    """
    Devuelve un link wa.me listo para abrir WhatsApp con el mensaje prellenado.
    - phone: con o sin '+'; debe incluir código de país (p. ej., '51' para Perú).
    """
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if not digits:
        digits = "51922360378"
        
    return f"https://wa.me/{digits}?text={quote_plus(text)}"

def send_waitlist_offer_test(wait_item, accept_url: str) -> str:
    """
    Versión de PRUEBA: solo construye el link de WhatsApp y lo devuelve.
    No llama a ningún proveedor.
    """
    paciente = wait_item.paciente
    nombre = f"{paciente.nombre} {paciente.apellidoPaterno}".strip()
    msg = (
        f"Hola {nombre}, se liberó un cupo. "
        f"Tienes {wait_item.ttl_respuesta_min} min para aceptarlo aquí: {accept_url}"
    )
    return build_wa_click_to_chat(getattr(paciente, "telefono", ""), msg)
