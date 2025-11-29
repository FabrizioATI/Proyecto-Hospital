from django.shortcuts import render, redirect
from django.contrib import messages
from database.models import Entidad, Rol, RolEntidad, NotificationPreference  


#Index
def index(request):
    return render(request, "home/index.html")

#Login
def login_view(request):
    ctx = {}
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
                    request.session["codigo_rol"] = rol_entidad.rol.codigo_rol
                    
                    if rol_entidad.rol.codigo_rol == "001":  # Doctor
                        messages.success(request, f"¡Bienvenido, {request.session['entidad_nombre']}!")
                        return redirect("index")
                    elif rol_entidad.rol.codigo_rol == "002":  # Paciente
                        messages.success(request, f"¡Bienvenido, {request.session['entidad_nombre']}!")
                        return redirect("index")
                    elif rol_entidad.rol.codigo_rol == "003":  # Administrador
                        messages.success(request, f"¡Bienvenido, {request.session['entidad_nombre']}!")
                        return redirect("index")
                    else:
                        messages.success(request, f"Rol no reconocido!")
                else:
                    messages.warning(request, "No tienes un rol asignado.")
            else:
                messages.error(request, "Contraseña no es corrects mira aqui.")
        except Entidad.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")

    return render(request, "accounts/login.html", ctx)

def home(request):
    if "entidad_id" in request.session:
        entidad = Entidad.objects.get(id=request.session["entidad_id"])
        return render(request, "doctor/lista_medicos.html", {"entidad": entidad})
    else:
        messages.warning(request, "Debes iniciar sesión para continuar.")
        return redirect("login")

def logout_view(request):
    request.session.flush() 
    messages.info(request, "Sesión cerrada correctamente.")
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
            messages.error(request, errors["dni"])

        if Entidad.objects.filter(correo=correo).exists():
            errors["correo"] = "Este correo ya está registrado."
            messages.error(request, errors["correo"])

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

            rol_paciente, created = Rol.objects.get_or_create(codigo_rol="002", nombre_rol="Paciente")
            RolEntidad.objects.create(entidad=entidad, rol=rol_paciente)
            messages.success(request, "Cuenta creada con éxito. Inicia sesión.")
             
            return redirect("login")

    return render(
        request,
        "accounts/register.html",
        {"errors": errors, "form_data": request.POST},
    )
    
def editar_perfil(request):
    if "entidad_id" not in request.session:
        messages.warning(request, "Debes iniciar sesión.")
        return redirect("login")

    entidad = Entidad.objects.get(id=request.session["entidad_id"])
    rol = RolEntidad.objects.filter(entidad=entidad).first()

    if not rol or rol.rol.codigo_rol != "002":
        messages.error(request, "No tienes permisos para editar este perfil.")
        return redirect("index")

    notif_pref, _ = NotificationPreference.objects.get_or_create(user=entidad)

    errors = {}

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellidoPaterno = request.POST.get("apellidoPaterno")
        apellidoMaterno = request.POST.get("apellidoMaterno")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")

        sms_consent = "sms_consent" in request.POST
        sms_language = request.POST.get("sms_language", notif_pref.sms_language)

        if Entidad.objects.filter(correo=correo).exclude(id=entidad.id).exists():
            errors["correo"] = "Este correo ya está registrado por otro usuario."

        if not errors:
            entidad.nombre = nombre
            entidad.apellidoPaterno = apellidoPaterno
            entidad.apellidoMaterno = apellidoMaterno
            entidad.telefono = telefono
            entidad.correo = correo
            entidad.save()

            notif_pref.sms_consent = sms_consent
            notif_pref.sms_language = sms_language
            notif_pref.save()

            request.session["entidad_nombre"] = (
                f"{entidad.nombre} {entidad.apellidoPaterno} {entidad.apellidoMaterno}"
            )

            messages.success(request, "Tu perfil fue actualizado correctamente.")

            # ⬇ REDIRECCIÓN A LA LISTA DE CLIENTES
            return redirect("lista_citas_paciente", entidad.id)

    return render(request, "accounts/editar_perfil.html", {
        "entidad": entidad,
        "errors": errors,
        "notif_pref": notif_pref
    })
