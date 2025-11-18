from database.models import WaitlistItem, Cita
from django.db import transaction

def procesar_cola(doctor_horario):
    # obtener siguiente en cola por prioridad + hora llegada
    item = (
        WaitlistItem.objects
        .filter(doctor_horario=doctor_horario, estado="pendiente")
        .select_related("paciente")
        .order_by("paciente__id")   # o fecha_solicitud
        .first()
    )

    if not item:
        return  # no hay pacientes

    with transaction.atomic():
        cita = Cita.objects.create(
            paciente=item.paciente,
            doctor=doctor_horario.doctor.entidad,
            doctor_horario=doctor_horario,
            motivo="Asignado desde cola",
            clasificacion="REGULAR"
        )

        item.estado = "aceptado"
        item.save()

        # Aquí puedes enviar EMAIL / WHATSAPP
        print(f"Notificando al paciente {item.paciente.nombre}")
