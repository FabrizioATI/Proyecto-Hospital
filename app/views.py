from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad, DoctorHorario, Horario
from django.contrib.auth import logout as django_logout 
from .forms import LoginForm 
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad
from .models import Cita, DoctorHorario 


def lista_medicos(request):
    medicos = DoctorDetalle.objects.select_related("entidad", "especialidad").all()
    return render(request, "doctor/lista_medicos.html", {"medicos": medicos})

def eliminar_medico(request, pk):
    doctor = get_object_or_404(DoctorDetalle, pk=pk)
    entidad = doctor.entidad
    doctor.delete()
    entidad.delete() 
    return redirect("lista_medicos")

def registrar_medico(request):
    errors = {}
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellidoPaterno = request.POST.get("apellidoPaterno")
        apellidoMaterno = request.POST.get("apellidoMaterno")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        telefono = request.POST.get("telefono")
        dni = request.POST.get("dni")

        especialidad_id = request.POST.get("especialidad")
        nro_colegiatura = request.POST.get("nro_colegiatura")

        if Entidad.objects.filter(dni=dni).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if DoctorDetalle.objects.filter(nro_colegiatura=nro_colegiatura).exists():
            errors["nro_colegiatura"] = "Este número de colegiatura ya está registrado."

        if not errors:
            entidad = Entidad.objects.create(
                nombre=nombre,
                apellidoPaterno=apellidoPaterno,
                apellidoMaterno=apellidoMaterno,
                correo=correo,
                contraseña=contraseña,
                telefono=telefono,
                dni=dni,
            )

            especialidad = Especialidad.objects.get(id=especialidad_id)
            DoctorDetalle.objects.create(
                entidad=entidad,
                especialidad=especialidad,
                nro_colegiatura=nro_colegiatura,
            )

            rol_doctor, created = Rol.objects.get_or_create(nombre_rol="doctor")
            RolEntidad.objects.create(entidad=entidad, rol=rol_doctor)

            messages.success(request, "Médico registrado correctamente.")
            return redirect("lista_medicos")

    especialidades = Especialidad.objects.all()
    return render(
        request,
        "doctor/registrar_medicos.html",
        {"especialidades": especialidades, "errors": errors},
    )

def editar_medico(request, pk):
    doctor = get_object_or_404(DoctorDetalle, pk=pk)
    errors = {}

    if request.method == "POST":
        dni = request.POST.get("dni")
        nro_colegiatura = request.POST.get("nro_colegiatura")

        if Entidad.objects.filter(dni=dni).exclude(id=doctor.entidad.id).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if DoctorDetalle.objects.filter(nro_colegiatura=nro_colegiatura).exclude(id=doctor.id).exists():
            errors["nro_colegiatura"] = "Este número de colegiatura ya está registrado."

        if not errors:
            doctor.entidad.nombre = request.POST.get("nombre")
            doctor.entidad.apellidoPaterno = request.POST.get("apellidoPaterno")
            doctor.entidad.apellidoMaterno = request.POST.get("apellidoMaterno")
            doctor.entidad.correo = request.POST.get("correo")
            doctor.entidad.telefono = request.POST.get("telefono")
            doctor.entidad.dni = dni
            doctor.entidad.save()

            especialidad_id = request.POST.get("especialidad")
            doctor.especialidad = Especialidad.objects.get(id=especialidad_id)
            doctor.nro_colegiatura = nro_colegiatura
            doctor.save()

            messages.success(request, "Médico actualizado correctamente.")
            return redirect("lista_medicos")

    especialidades = Especialidad.objects.all()
    return render(
        request,
        "doctor/editar_medico.html",
        {"doctor": doctor, "especialidades": especialidades, "errors": errors},
    )




# CRUD de Citas

def lista_citas(request):
    citas = Cita.objects.select_related("paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario").all()
    return render(request, "citas/lista_citas.html", {"citas": citas})


def registrar_cita(request):
    errors = {}
    if request.method == "POST":
        paciente_id = request.POST.get("paciente")
        doctor_horario_id = request.POST.get("doctor_horario")
        estado = request.POST.get("estado")
        motivo = request.POST.get("motivo")

        # Validaciones
        if not paciente_id:
            errors["paciente"] = "Debe seleccionar un paciente."
        if not doctor_horario_id:
            errors["doctor_horario"] = "Debe seleccionar un horario de doctor."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        if not errors:
            paciente = Entidad.objects.get(id=paciente_id)
            doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)

            Cita.objects.create(
                paciente=paciente,
                doctor_horario=doctor_horario,
                estado=estado,
                motivo=motivo,
            )
            messages.success(request, "Cita registrada correctamente.")
            return redirect("lista_citas")

    pacientes = Entidad.objects.all()
    horarios = DoctorHorario.objects.select_related("doctor__entidad", "horario").all()

    return render(
        request,
        "citas/registrar_cita.html",
        {"pacientes": pacientes, "horarios": horarios, "errors": errors},
    )


def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    errors = {}

    if request.method == "POST":
        paciente_id = request.POST.get("paciente")
        doctor_horario_id = request.POST.get("doctor_horario")
        estado = request.POST.get("estado")
        motivo = request.POST.get("motivo")

        if not errors:
            cita.paciente = Entidad.objects.get(id=paciente_id)
            cita.doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
            cita.estado = estado
            cita.motivo = motivo
            cita.save()
            messages.success(request, "Cita actualizada correctamente.")
            return redirect("lista_citas")

    pacientes = Entidad.objects.all()
    horarios = DoctorHorario.objects.select_related("doctor__entidad", "horario").all()

    return render(
        request,
        "citas/editar_cita.html",
        {"cita": cita, "pacientes": pacientes, "horarios": horarios, "errors": errors},
    )


def eliminar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    cita.delete()
    messages.success(request, "Cita eliminada correctamente.")
    return redirect("lista_citas")

def login_view(request):
    if request.method == "POST":
        dni = request.POST.get("dni")
        password = request.POST.get("contraseña")

        try:
            entidad = Entidad.objects.get(dni=dni)
            if entidad.contraseña == password:
                request.session["entidad_id"] = entidad.id

                rol_entidad = RolEntidad.objects.filter(entidad=entidad).first()

                if rol_entidad:
                    if rol_entidad.rol.id == 1:  # Doctor
                        return redirect("admin_home")
                    elif rol_entidad.rol.id == 2:  # Paciente
                        return redirect("home")
                    else:
                        messages.error(request, "Rol no reconocido")
                else:
                    messages.error(request, "No tienes un rol asignado")

            else:
                messages.error(request, "Contraseña incorrecta")
        except Entidad.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    return render(request, "accounts/login.html")

def home(request):
    if "entidad_id" in request.session:
        entidad = Entidad.objects.get(id=request.session["entidad_id"])
        return render(request, "doctor/lista_medicos.html", {"entidad": entidad})
    else:
        return redirect("login")

def logout_view(request):
    # django_logout(request)
    return redirect('login')

def register(request):
    errors = {}
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellidoPaterno = request.POST.get("apellidoPaterno")
        apellidoMaterno = request.POST.get("apellidoMaterno")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        telefono = request.POST.get("telefono")
        dni = request.POST.get("dni")

        # Validaciones
        if Entidad.objects.filter(dni=dni).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if Entidad.objects.filter(correo=correo).exists():
            errors["correo"] = "Este correo ya está registrado."

        if not errors:
            entidad = Entidad.objects.create(
                nombre=nombre,
                apellidoPaterno=apellidoPaterno,
                apellidoMaterno=apellidoMaterno,
                correo=correo,
                contraseña=contraseña,
                telefono=telefono,
                dni=dni,
            )

            rol_paciente, created = Rol.objects.get_or_create(nombre_rol="Paciente")
            RolEntidad.objects.create(entidad=entidad, rol=rol_paciente)

            return redirect("login")

    return render(
        request,
        "accounts/register.html",
        {"errors": errors, "form_data": request.POST},
    )

def registrarHorarioMedico(request, pk):
    doctor = get_object_or_404(DoctorDetalle, pk=pk)
    times = Horario.objects.all()

    if request.method == "POST":
        fecha = request.POST.get("date")
        hora = request.POST.get("time")
        horario = Horario.objects.filter(fecha=fecha, hora_inicio=hora).first()
        if not horario:
            messages.error(request, "No existe un horario con esa fecha y hora.")
        elif DoctorHorario.objects.filter(doctor=doctor, horario=horario).exists():
            messages.error(request, "El médico ya tiene asignado ese horario.")
        else:
            DoctorHorario.objects.create(doctor=doctor, horario=horario)
            messages.success(request, "Horario asignado correctamente.")
            return redirect("lista_medicos")

    context = {
        "doc": doctor,
        "times": times,
    }
    return render(request, "doctor/horario_medicos.html", context)
    return render(request, "doctor/horario_medicos.html", context)


def lista_pacientes(request):
    pacientes = Entidad.objects.filter(rolentidad__rol__nombre_rol="paciente")
    return render(request, "paciente/lista_pacientes.html", {
        "pacientes": pacientes,
        "segment": "pacientes"
    })


def registrar_paciente(request):
    errors = {}
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellidoPaterno = request.POST.get("apellidoPaterno")
        apellidoMaterno = request.POST.get("apellidoMaterno")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        telefono = request.POST.get("telefono")
        dni = request.POST.get("dni")

        if Entidad.objects.filter(dni=dni).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if not errors:
            entidad = Entidad.objects.create(
                nombre=nombre,
                apellidoPaterno=apellidoPaterno,
                apellidoMaterno=apellidoMaterno,
                correo=correo,
                contraseña=contraseña,
                telefono=telefono,
                dni=dni,
            )

            rol_paciente, _ = Rol.objects.get_or_create(nombre_rol="paciente")
            RolEntidad.objects.create(entidad=entidad, rol=rol_paciente)

            messages.success(request, "Paciente registrado correctamente.")
            return redirect("lista_pacientes")

    return render(request, "paciente/registrar_pacientes.html", {
        "errors": errors,
        "segment": "pacientes"
    })


def editar_paciente(request, pk):
    paciente = get_object_or_404(Entidad, pk=pk)
    errors = {}

    if request.method == "POST":
        dni = request.POST.get("dni")
        if Entidad.objects.filter(dni=dni).exclude(id=paciente.id).exists():
            errors["dni"] = "Este DNI ya está registrado."

        if not errors:
            paciente.nombre = request.POST.get("nombre")
            paciente.apellidoPaterno = request.POST.get("apellidoPaterno")
            paciente.apellidoMaterno = request.POST.get("apellidoMaterno")
            paciente.correo = request.POST.get("correo")
            paciente.telefono = request.POST.get("telefono")
            paciente.dni = dni
            paciente.save()

            messages.success(request, "Paciente actualizado correctamente.")
            return redirect("lista_pacientes")

    return render(request, "paciente/editar_paciente.html", {
        "paciente": paciente,
        "errors": errors,
        "segment": "pacientes"
    })


def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Entidad, pk=pk)
    paciente.delete()
    return redirect("lista_pacientes")

@login_required
def home(request):
    return render(request, 'home/index.html') 

