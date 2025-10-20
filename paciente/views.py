from django.shortcuts import render, redirect, get_object_or_404
from database.models import Entidad, Rol, RolEntidad


#Index
def index(request):
    return render(request, "home/index.html")

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

            rol_paciente, _ = Rol.objects.get_or_create(nombre_rol="Paciente")
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
