from datetime import datetime, timedelta, time
from database.models import Horario, DoctorDetalle, DoctorHorario

def generar_horarios_automaticos(
    dias=30,
    hora_inicio=time(8, 0),
    hora_fin=time(13, 0),
    duracion_min=20
):
    now = datetime.now().date()
    rango = hora_fin.hour * 60 + hora_fin.minute
    inicio = hora_inicio.hour * 60 + hora_inicio.minute

    for doctor in DoctorDetalle.objects.all():
        for d in range(dias):
            fecha = now + timedelta(days=d)

            t = inicio
            while t < rango:
                hi = time(t // 60, t % 60)
                hf_min = t + duracion_min
                hf = time(hf_min // 60, hf_min % 60)

                # crear horario general
                horario, _ = Horario.objects.get_or_create(
                    fecha=fecha,
                    hora_inicio=hi,
                    hora_fin=hf
                )

                # asignar a doctor
                DoctorHorario.objects.get_or_create(
                    doctor=doctor,
                    horario=horario
                )

                t += duracion_min
