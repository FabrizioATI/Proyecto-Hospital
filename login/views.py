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