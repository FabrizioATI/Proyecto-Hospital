from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad, DoctorHorario, Horario
from django.contrib.auth import logout as django_logout 
from .forms import LoginForm 

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

