from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad, DoctorHorario, Horario
from django.contrib.auth import logout as django_logout 
from .forms import LoginForm 
from .models import Entidad, DoctorDetalle, Especialidad, Rol, RolEntidad
from .models import Cita, DoctorHorario 

#Index
def index(request):
    return render(request, "home/index.html")

# CRUD de Medicos
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

            # messages.success(request, "Médico registrado correctamente.")
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

            # messages.success(request, "Médico actualizado correctamente.")
            return redirect("lista_medicos")

    especialidades = Especialidad.objects.all()
    return render(
        request,
        "doctor/editar_medico.html",
        {"doctor": doctor, "especialidades": especialidades, "errors": errors},
    )

# CRUD de Citas
def lista_citas_paciente(request, paciente_id):
    citas = Cita.objects.select_related(
        "paciente", "doctor_horario__doctor__entidad", "doctor_horario__horario"
    ).filter(paciente_id=paciente_id)

    return render(request, "citas/lista_citas.html", {"citas": citas})

def registrar_cita_paciente(request, paciente_id):
    paciente = get_object_or_404(Entidad, id=paciente_id)
    errors = {}

    especialidad_id = request.GET.get("especialidad")
    doctor_id = request.GET.get("doctor")

    if request.method == "POST":
        doctor_horario_id = request.POST.get("doctor_horario")
        motivo = request.POST.get("motivo")

        if not doctor_horario_id:
            errors["doctor_horario"] = "Debe seleccionar un horario de doctor."
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."

        if not errors:
            doctor_horario = DoctorHorario.objects.get(id=doctor_horario_id)
            Cita.objects.create(
                paciente=paciente,               # ← El paciente viene de la sesión
                doctor_horario=doctor_horario,
                motivo=motivo,
                estado="pendiente",
            )
            # messages.success(request, "Cita registrada correctamente.")
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad_id=especialidad_id) if especialidad_id else []
    horarios = DoctorHorario.objects.filter(doctor_id=doctor_id).select_related("horario") if doctor_id else []

    return render(request, "citas/registrar_cita.html", {
        "paciente": paciente,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "errors": errors,
        "selected_esp": int(especialidad_id) if especialidad_id else None,
        "selected_doc": int(doctor_id) if doctor_id else None,
    })

def editar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    errors = {}

    # Para mostrar las listas
    especialidades = Especialidad.objects.all()
    doctores = DoctorDetalle.objects.filter(especialidad=cita.doctor_horario.doctor.especialidad)
    horarios = DoctorHorario.objects.filter(doctor=cita.doctor_horario.doctor).select_related("horario")

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        if not motivo:
            errors["motivo"] = "Debe ingresar un motivo."
        else:
            cita.motivo = motivo
            cita.save()
            # messages.success(request, "Cita actualizada correctamente.")
            return redirect("lista_citas_paciente", paciente_id=paciente_id)

    return render(request, "citas/editar_cita.html", {
        "cita": cita,
        "especialidades": especialidades,
        "doctores": doctores,
        "horarios": horarios,
        "selected_esp": cita.doctor_horario.doctor.especialidad.id,
        "selected_doc": cita.doctor_horario.doctor.id,
        "errors": errors,
    })

def eliminar_cita_paciente(request, paciente_id, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente_id=paciente_id)
    cita.delete()
    # messages.success(request, "Cita eliminada correctamente.")
    return redirect("lista_citas_paciente", paciente_id=paciente_id)

def lista_citas_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorDetalle, entidad_id=doctor_id)
    citas = Cita.objects.filter(doctor_horario__doctor=doctor).select_related(
        "paciente", "doctor_horario__horario"
    ).order_by("doctor_horario__horario__fecha", "doctor_horario__horario__hora_inicio")

    return render(request, "citas/lista_citas.html", {
        "citas": citas,
        "doctor": doctor,
        "tipo_usuario": "doctor"
    })

# CRUD de Pacientes
def lista_pacientes(request):
    pacientes = Entidad.objects.filter(rolentidad__rol__nombre_rol="Paciente")
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

            # messages.success(request, "Paciente registrado correctamente.")
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

            # messages.success(request, "Paciente actualizado correctamente.")
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

#Login
def login_view(request):
    if request.method == "POST":
        dni = request.POST.get("dni")
        password = request.POST.get("contraseña")

        try:
            entidad = Entidad.objects.get(dni=dni)
            if entidad.contraseña == password:
                # Guardas ID y nombre en la sesión
                request.session["entidad_id"] = entidad.id
                request.session["entidad_nombre"] = entidad.nombre + " " + entidad.apellidoPaterno + " " + entidad.apellidoMaterno

                rol_entidad = RolEntidad.objects.filter(entidad=entidad).first()

                if rol_entidad:
                    request.session["rol_id"] = rol_entidad.rol.id

                    if rol_entidad.rol.id == 1:  # Doctor
                        return redirect("index")
                    elif rol_entidad.rol.id == 2:  # Paciente
                        return redirect("index")
                    elif rol_entidad.rol.id == 3:  # Administrador
                        return redirect("index")
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

#CRUD Mantenimiento
def mantenimiento_roles_especialidades(request):
    if request.method == "POST":
        accion = request.POST.get("accion")

        # ----------- ROLES -----------
        if accion == "agregar_rol":
            nombre = request.POST.get("nuevo_rol")
            if nombre:
                Rol.objects.create(nombre_rol=nombre)

        elif accion == "editar_rol":
            rol_id = request.POST.get("rol_id")
            nuevo_nombre = request.POST.get("editar_rol")
            if rol_id and nuevo_nombre:
                rol = Rol.objects.get(id=rol_id)
                rol.nombre_rol = nuevo_nombre
                rol.save()

        elif accion == "eliminar_rol":
            rol_id = request.POST.get("rol_id")
            if rol_id:
                Rol.objects.filter(id=rol_id).delete()

        # ----------- ESPECIALIDADES -----------
        elif accion == "agregar_especialidad":
            nombre = request.POST.get("nueva_especialidad")
            if nombre:
                Especialidad.objects.create(nombre=nombre)

        elif accion == "editar_especialidad":
            esp_id = request.POST.get("especialidad_id")
            nuevo_nombre = request.POST.get("editar_especialidad")
            if esp_id and nuevo_nombre:
                esp = Especialidad.objects.get(id=esp_id)
                esp.nombre = nuevo_nombre
                esp.save()

        elif accion == "eliminar_especialidad":
            esp_id = request.POST.get("especialidad_id")
            if esp_id:
                Especialidad.objects.filter(id=esp_id).delete()

        # Redirigir para evitar reenvío de formulario
        return redirect("mantenimiento_roles_especialidades")

    # GET: cargar listas
    roles = Rol.objects.all()
    especialidades = Especialidad.objects.all()

    return render(request, "mantenimiento/mantenimiento_roles_especialidades.html", {
        "roles": roles,
        "especialidades": especialidades,
    })