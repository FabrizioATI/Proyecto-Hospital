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
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dni = form.cleaned_data['dni']
        password = form.cleaned_data['password']
        user = authenticate(request, username=dni, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "¡Bienvenido!")
            return redirect(request.GET.get('next') or 'home')
        messages.error(request, "DNI o contraseña inválidos.")
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    django_logout(request)
    return redirect('login')

def register(request):
  if request.method == 'POST':
    user_status = request.POST.get('user_config')
    first_name = request.POST.get('user_firstname')
    last_name = request.POST.get('user_lastname')
    profile_pic = ""

    if "profile_pic" in request.FILES:
      profile_pic = request.FILES['profile_pic']

    username = request.POST.get('user_id')
    email = request.POST.get('email')
    gender = request.POST.get('user_gender')
    birthday = request.POST.get("birthday")
    password = request.POST.get('password')
    confirm_password = request.POST.get('conf_password')
    address_line = request.POST.get('address_line')
    region = request.POST.get('region')
    city = request.POST.get('city')
    pincode = request.POST.get('pincode')

    if len(password) < 6:
      messages.error(request, 'Password must be at least 6 characters long.')
      return render(request, 'users/register.html', context={'user_config': user_status, 'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender, 'address_line': address_line, 'region': region, 'city': city, 'pincode': pincode})

    if password != confirm_password:
      messages.error(request, 'Passwords do not match.')
      return render(request, 'users/register.html', context={'user_config': user_status, 'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender, 'address_line': address_line, 'region': region, 'city': city, 'pincode': pincode})

    if Users.objects.filter(username=username).exists():
      messages.error(request, 'Username already exists. Try again with a different username.')
      return render(request, 'users/register.html', context={'user_config': user_status, 'user_firstname': first_name, 'user_lastname': last_name, 'user_id': username, 'email': email, 'user_gender': gender, 'address_line': address_line, 'region': region, 'city': city, 'pincode': pincode})

    address = Address.objects.create(address_line=address_line, region=region,city=city, code_postal=pincode)

    user = Users.objects.create_user(
      first_name=first_name,
      last_name=last_name,
      profile_avatar=profile_pic,
      username=username,
      email=email,
      gender=gender,
      birthday=birthday,
      password=password,
      id_address=address,
      is_doctor=(user_status == 'Doctor')
    )
      
    user.save()

    if user_status == 'Doctor':
      specialty = request.POST.get('Speciality')
      specialty_name = Specialty.objects.get(name=specialty)
      bio = request.POST.get('bio')
      doctor = Doctors.objects.create(user=user, specialty=specialty_name, bio=bio)
      doctor.save()
        
    elif user_status == 'Patient':
        insurance = request.POST.get('insurance')
        patient = Patients.objects.create(user=user, insurance=insurance)
        patient.save()

    messages.success(request, 'Your account has been successfully registered. Please login.', extra_tags='success')

  return render(request, 'accounts/register.html')

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