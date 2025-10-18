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