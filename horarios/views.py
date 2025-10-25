from datetime import datetime, timedelta
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from database.models import DoctorDetalle, Horario, DoctorHorario


#Index
def index(request):
    return render(request, "home/index.html")

def build_time_slots(start="06:00", end="22:00", step=30):
    t0 = datetime.strptime(start, "%H:%M")
    t1 = datetime.strptime(end, "%H:%M")
    slots = []
    while t0 <= t1:
        slots.append(t0.strftime("%H:%M"))
        t0 += timedelta(minutes=step)
    return slots

#CRUD Horario Medico
def lista_horarios_medico(request):
    # Trae todos los horarios con sus doctores
    horarios = DoctorHorario.objects.select_related('doctor', 'horario').order_by('horario__fecha', 'horario__hora_inicio')
    return render(request, 'doctor_horario/lista_horario_medicos.html', {'horarios': horarios})

def registrar_horario_medico(request):
    doctores = DoctorDetalle.objects.all()
    time_slots = build_time_slots("06:00", "22:00", 30)
    errors = {}
    info = {}

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        fecha_str = request.POST.get("fecha")
        hi_str = request.POST.get("hora_inicio")
        hf_str = request.POST.get("hora_fin")

        # Validaciones básicas
        if not all([doctor_id, fecha_str, hi_str, hf_str]):
            errors["form"] = "Completa todos los campos."
        else:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                hi = datetime.strptime(hi_str, "%H:%M").time()
                hf = datetime.strptime(hf_str, "%H:%M").time()
            except ValueError:
                errors["form"] = "Formato de fecha/hora inválido."

        if not errors:
            if hi >= hf:
                errors["rango"] = "La hora fin debe ser mayor que la hora inicio."
            # Solo :00 o :30
            if hi.minute not in (0, 30) or hf.minute not in (0, 30):
                errors["paso"] = "Usa intervalos de 30 minutos (:00 o :30)."

        if not errors:
            start_dt = datetime.combine(fecha, hi)
            end_dt = datetime.combine(fecha, hf)

            conflictos = []
            creados = 0

            try:
                with transaction.atomic():
                    while start_dt < end_dt:
                        slot_start = start_dt.time()
                        slot_end_dt = start_dt + timedelta(minutes=30)
                        slot_end = slot_end_dt.time()

                        # Chequea traslape: (nuevo_inicio < existente_fin) y (nuevo_fin > existente_inicio)
                        existe = DoctorHorario.objects.filter(
                            doctor_id=doctor_id,
                            horario__fecha=fecha,
                            horario__hora_inicio__lt=slot_end,
                            horario__hora_fin__gt=slot_start,
                        ).exists()

                        if existe:
                            conflictos.append(f"{slot_start.strftime('%H:%M')}–{slot_end.strftime('%H:%M')}")
                        else:
                            h = Horario.objects.create(
                                fecha=fecha,
                                hora_inicio=slot_start,
                                hora_fin=slot_end
                            )
                            DoctorHorario.objects.create(doctor_id=doctor_id, horario=h)
                            creados += 1

                        start_dt = slot_end_dt
            except Exception as e:
                errors["form"] = f"Ocurrió un error guardando los horarios: {e}"

            if conflictos and not creados:
                errors["conflictos"] = "Ya existen turnos que chocan: " + ", ".join(conflictos)
            elif conflictos and creados:
                info["parcial"] = f"Se crearon {creados} turnos. Estos chocaron y no se crearon: " + ", ".join(conflictos)
                return redirect("lista_horarios_medico")
            else:
                # todo ok, sin conflictos
                return redirect("lista_horarios_medico")

    return render(request, "doctor_horario/registrar_horario_medicos.html", {
        "doctores": doctores,
        "errors": errors,
        "info": info,
        "time_slots": time_slots
    })

def editar_horario_medico(request, pk):
    # Obtenemos el registro de DoctorHorario
    doctor_horario = get_object_or_404(DoctorHorario, pk=pk)
    
    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # Actualizamos la relación Doctor
        doctor = get_object_or_404(DoctorDetalle, pk=doctor_id)
        doctor_horario.doctor = doctor

        # Actualizamos la información de Horario
        horario = doctor_horario.horario
        horario.fecha = fecha
        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
        horario.save()

        # Guardamos la relación DoctorHorario
        doctor_horario.save()

        # messages.success(request, "Horario actualizado correctamente.")
        return redirect('lista_horarios_medico')

    # GET: mostramos el formulario con los datos actuales
    doctores = DoctorDetalle.objects.all()
    return render(request, "doctor_horario/editar_horario_medico.html", {
        "doctor_horario": doctor_horario,
        "doctores": doctores
    })

def eliminar_horario_medico(request, pk):
    doctor_horario = get_object_or_404(DoctorHorario, pk=pk)
    horario = doctor_horario.horario  # Obtenemos el Horario asociado
    doctor_horario.delete()           # Eliminamos la relación
    horario.delete()                   # Eliminamos el horario en sí
    return redirect("lista_horarios_medico")
