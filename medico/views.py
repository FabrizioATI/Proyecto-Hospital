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