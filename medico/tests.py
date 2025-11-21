from django.test import TestCase, Client
from django.urls import reverse

from database.models import (
    Entidad,
    Rol,
    RolEntidad,
    Especialidad,
    DoctorDetalle,
)


class ListaMedicosViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Simular una Entidad "logueada" en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_med@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00010000",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        # Crear especialidad y médico
        self.especialidad = Especialidad.objects.create(
            nombre="Cardiología"
        )

        self.entidad_medico = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Médico",
            apellidoMaterno="Perez",
            correo="medico@example.com",
            contraseña="123456",
            telefono="999888777",
            dni="12345678",
        )

        self.doctor = DoctorDetalle.objects.create(
            entidad=self.entidad_medico,
            especialidad=self.especialidad,
            nro_colegiatura="COL-001",
        )

    def test_lista_medicos_usa_template_y_contexto(self):
        response = self.client.get(reverse("lista_medicos"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/lista_medicos.html")

        medicos = response.context["medicos"]
        self.assertIn(self.doctor, medicos)


class RegistrarMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Simular Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_reg_med@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00010001",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        # Especialidad existente para usar en el formulario
        self.especialidad = Especialidad.objects.create(
            nombre="Pediatría"
        )

    def test_registro_medico_get_usa_template_y_especialidades(self):
        response = self.client.get(reverse("registro_medico"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/registrar_medicos.html")

        especialidades = response.context.get("especialidades")
        self.assertIsNotNone(especialidades)
        self.assertIn(self.especialidad, especialidades)

    def test_registro_medico_post_valido_crea_entidad_doctor_y_rol(self):
        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Doctor",
            "apellidoMaterno": "Apellido",
            "correo": "nuevo_doctor@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "22223333",
            "especialidad": str(self.especialidad.id),
            "nro_colegiatura": "COL-999",
        }

        response = self.client.post(reverse("registro_medico"), data)

        # Debe redirigir a lista_medicos
        self.assertRedirects(response, reverse("lista_medicos"))

        # Se creó la Entidad
        entidad = Entidad.objects.get(dni="22223333")
        self.assertEqual(entidad.correo, "nuevo_doctor@example.com")

        # Se creó el DoctorDetalle
        doctor = DoctorDetalle.objects.get(entidad=entidad)
        self.assertEqual(doctor.nro_colegiatura, "COL-999")
        self.assertEqual(doctor.especialidad, self.especialidad)

        # Se creó/asignó el rol Doctor (por nombre_rol)
        rol_doctor = Rol.objects.get(nombre_rol="Doctor")
        rel = RolEntidad.objects.get(entidad=entidad, rol=rol_doctor)
        self.assertIsNotNone(rel)

    def test_registro_medico_post_dni_duplicado_muestra_error(self):
        # Entidad existente con mismo DNI
        Entidad.objects.create(
            nombre="Existente",
            apellidoPaterno="Medico",
            apellidoMaterno="Apellido",
            correo="existente_medico@example.com",
            contraseña="123456",
            telefono="777777777",
            dni="99990000",
        )

        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Doctor",
            "apellidoMaterno": "Apellido",
            "correo": "nuevo@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "99990000",  # mismo DNI
            "especialidad": str(self.especialidad.id),
            "nro_colegiatura": "COL-100",
        }

        response = self.client.post(reverse("registro_medico"), data)

        # No debe redirigir: se queda en la misma página
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/registrar_medicos.html")

        errors = response.context.get("errors", {})
        self.assertIn("dni", errors)
        self.assertEqual(errors["dni"], "Este DNI ya está registrado.")

        # Solo debe existir una entidad con ese DNI
        self.assertEqual(Entidad.objects.filter(dni="99990000").count(), 1)
        # Y no debe haberse creado DoctorDetalle con ese nro_colegiatura
        self.assertFalse(DoctorDetalle.objects.filter(nro_colegiatura="COL-100").exists())

    def test_registro_medico_post_colegiatura_duplicada_muestra_error(self):
        # Doctor existente con número de colegiatura
        entidad_existente = Entidad.objects.create(
            nombre="Doc",
            apellidoPaterno="Existente",
            apellidoMaterno="Apellido",
            correo="doc_existente@example.com",
            contraseña="123456",
            telefono="666666666",
            dni="88880000",
        )
        DoctorDetalle.objects.create(
            entidad=entidad_existente,
            especialidad=self.especialidad,
            nro_colegiatura="COL-200",
        )

        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Doctor",
            "apellidoMaterno": "Apellido",
            "correo": "nuevo2@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "12349876",
            "especialidad": str(self.especialidad.id),
            "nro_colegiatura": "COL-200",  # repetido
        }

        response = self.client.post(reverse("registro_medico"), data)

        # No debe redirigir: se queda en el formulario
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/registrar_medicos.html")

        errors = response.context.get("errors", {})
        self.assertIn("nro_colegiatura", errors)
        self.assertEqual(errors["nro_colegiatura"], "Este número de colegiatura ya está registrado.")

        # Solo debe haber un doctor con esa colegiatura
        self.assertEqual(DoctorDetalle.objects.filter(nro_colegiatura="COL-200").count(), 1)


class EditarMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_edit_med@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00010002",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        # Especialidades
        self.especialidad1 = Especialidad.objects.create(nombre="Neurología")
        self.especialidad2 = Especialidad.objects.create(nombre="Dermatología")

        self.entidad_medico = Entidad.objects.create(
            nombre="Medico",
            apellidoPaterno="Original",
            apellidoMaterno="Apellido",
            correo="medico_edit@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="55551111",
        )

        self.doctor = DoctorDetalle.objects.create(
            entidad=self.entidad_medico,
            especialidad=self.especialidad1,
            nro_colegiatura="COL-E001",
        )

    def test_editar_medico_get_usa_template_y_contexto(self):
        url = reverse("editar_medico", args=[self.doctor.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/editar_medico.html")
        self.assertEqual(response.context.get("doctor"), self.doctor)

        especialidades = response.context.get("especialidades")
        self.assertIn(self.especialidad1, especialidades)
        self.assertIn(self.especialidad2, especialidades)

    def test_editar_medico_post_valido_actualiza_y_redirige(self):
        url = reverse("editar_medico", args=[self.doctor.id])
        data = {
            "nombre": "Medico Editado",
            "apellidoPaterno": "NuevoAp",
            "apellidoMaterno": "NuevoAm",
            "correo": "editado_med@example.com",
            "telefono": "111111111",
            "dni": "99998888",
            "especialidad": str(self.especialidad2.id),
            "nro_colegiatura": "COL-E999",
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("lista_medicos"))

        self.doctor.refresh_from_db()
        self.entidad_medico.refresh_from_db()

        self.assertEqual(self.entidad_medico.nombre, "Medico Editado")
        self.assertEqual(self.entidad_medico.apellidoPaterno, "NuevoAp")
        self.assertEqual(self.entidad_medico.apellidoMaterno, "NuevoAm")
        self.assertEqual(self.entidad_medico.correo, "editado_med@example.com")
        self.assertEqual(self.entidad_medico.telefono, "111111111")
        self.assertEqual(self.entidad_medico.dni, "99998888")

        self.assertEqual(self.doctor.nro_colegiatura, "COL-E999")
        self.assertEqual(self.doctor.especialidad, self.especialidad2)

    def test_editar_medico_post_dni_duplicado_no_actualiza(self):
        # Otro Entidad con mismo DNI que intentaremos usar
        otro = Entidad.objects.create(
            nombre="Otro",
            apellidoPaterno="Doc",
            apellidoMaterno="Apellido",
            correo="otro_doc@example.com",
            contraseña="123456",
            telefono="222222222",
            dni="12121212",
        )

        url = reverse("editar_medico", args=[self.doctor.id])
        data = {
            "nombre": "Intento Editar",
            "apellidoPaterno": "X",
            "apellidoMaterno": "Y",
            "correo": "intentando_med@example.com",
            "telefono": "333333333",
            "dni": "12121212",  # DNI de 'otro'
            "especialidad": str(self.especialidad2.id),
            "nro_colegiatura": "COL-E002",
        }

        response = self.client.post(url, data)

        # No redirige, se queda en editar
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/editar_medico.html")

        errors = response.context.get("errors", {})
        self.assertIn("dni", errors)
        self.assertEqual(errors["dni"], "Este DNI ya está registrado.")

        # El médico original no debe haber cambiado al DNI duplicado
        self.entidad_medico.refresh_from_db()
        self.assertEqual(self.entidad_medico.dni, "55551111")

    def test_editar_medico_post_colegiatura_duplicada_no_actualiza(self):
        # Otro doctor con la misma colegiatura
        entidad_otro = Entidad.objects.create(
            nombre="OtroMed",
            apellidoPaterno="Doc",
            apellidoMaterno="Apellido",
            correo="otro_med@example.com",
            contraseña="123456",
            telefono="444444444",
            dni="34343434",
        )
        DoctorDetalle.objects.create(
            entidad=entidad_otro,
            especialidad=self.especialidad1,
            nro_colegiatura="COL-DUP",
        )

        url = reverse("editar_medico", args=[self.doctor.id])
        data = {
            "nombre": "Intento Editar",
            "apellidoPaterno": "X",
            "apellidoMaterno": "Y",
            "correo": "intentando_med2@example.com",
            "telefono": "555555555",
            "dni": "55551111",  # deja el mismo
            "especialidad": str(self.especialidad2.id),
            "nro_colegiatura": "COL-DUP",  # colegiatura existente
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/editar_medico.html")

        errors = response.context.get("errors", {})
        self.assertIn("nro_colegiatura", errors)
        self.assertEqual(errors["nro_colegiatura"], "Este número de colegiatura ya está registrado.")

        # El doctor original no debe haber cambiado su nro_colegiatura
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.nro_colegiatura, "COL-E001")


class EliminarMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_del_med@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00010003",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        self.especialidad = Especialidad.objects.create(nombre="Oncología")

        self.entidad_medico = Entidad.objects.create(
            nombre="MedicoEliminar",
            apellidoPaterno="Ap",
            apellidoMaterno="Am",
            correo="del_med@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="89898989",
        )
        self.doctor = DoctorDetalle.objects.create(
            entidad=self.entidad_medico,
            especialidad=self.especialidad,
            nro_colegiatura="COL-DEL",
        )

    def test_eliminar_medico_borra_doctor_y_entidad_y_redirige(self):
        url = reverse("eliminar_medico", args=[self.doctor.id])

        response = self.client.get(url)

        # Redirige a lista_medicos
        self.assertRedirects(response, reverse("lista_medicos"))

        # Doctor y Entidad deben haber sido eliminados
        self.assertFalse(DoctorDetalle.objects.filter(id=self.doctor.id).exists())
        self.assertFalse(Entidad.objects.filter(id=self.entidad_medico.id).exists())
