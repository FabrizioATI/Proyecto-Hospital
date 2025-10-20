from django.shortcuts import render, redirect, get_object_or_404
from database.models import Entidad, Rol, RolEntidad, Especialidad, DoctorDetalle


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

            rol_doctor, created = Rol.objects.get_or_create(nombre_rol="Doctor")
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