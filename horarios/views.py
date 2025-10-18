from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad, DoctorHorario, Horario
from django.contrib.auth import logout as django_logout 
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad
from .models import Cita, DoctorHorario 

#Index
def index(request):
    return render(request, "home/index.html")

#CRUD Horario Medico
def lista_horarios_medico(request):
    # Trae todos los horarios con sus doctores
    horarios = DoctorHorario.objects.select_related('doctor', 'horario').order_by('horario__fecha', 'horario__hora_inicio')
    return render(request, 'doctor_horario/lista_horario_medicos.html', {'horarios': horarios})

def registrar_horario_medico(request):
    # Traer todos los doctores para el <select> del formulario
    doctores = DoctorDetalle.objects.all()

    if request.method == "POST":
        # Obtener datos del formulario
        doctor_id = request.POST.get("doctor")
        fecha = request.POST.get("fecha")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # Validar que todos los campos tengan valor
        if doctor_id and fecha and hora_inicio and hora_fin:
            # Crear el horario
            horario = Horario.objects.create(
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            # Asociar el horario con el doctor
            DoctorHorario.objects.create(
                doctor_id=doctor_id,
                horario=horario
            )
            # Redirigir a la lista de horarios (ajusta la URL según tu proyecto)
            return redirect("lista_horarios_medico")

    # Renderizar el formulario pasando los doctores
    return render(request, "doctor_horario/registrar_horario_medicos.html", {
        "doctores": doctores
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
