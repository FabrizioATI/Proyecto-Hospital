from django.test import TestCase, Client
from django.urls import reverse

from database.models import Entidad, Rol, RolEntidad


class ListaPacientesViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Simular una Entidad "logueada" en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00000000",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        # Rol Paciente y otro rol cualquiera (Doctor)
        self.rol_paciente = Rol.objects.create(
            codigo_rol="002",
            nombre_rol="Paciente",
        )
        self.rol_doctor = Rol.objects.create(
            codigo_rol="001",
            nombre_rol="Doctor",
        )

        # Paciente
        self.paciente = Entidad.objects.create(
            nombre="Paciente",
            apellidoPaterno="Uno",
            apellidoMaterno="Apellido",
            correo="paciente@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="11111111",
        )
        RolEntidad.objects.create(entidad=self.paciente, rol=self.rol_paciente)

        # No-paciente (Doctor)
        self.doctor = Entidad.objects.create(
            nombre="Doctor",
            apellidoPaterno="Dos",
            apellidoMaterno="Apellido",
            correo="doctor@example.com",
            contraseña="123456",
            telefono="888888888",
            dni="22222222",
        )
        RolEntidad.objects.create(entidad=self.doctor, rol=self.rol_doctor)

    def test_lista_pacientes_filtra_solo_pacientes_y_usa_template(self):
        response = self.client.get(reverse("lista_pacientes"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/lista_pacientes.html")

        pacientes = response.context["pacientes"]
        self.assertIn(self.paciente, pacientes)
        self.assertNotIn(self.doctor, pacientes)

        self.assertEqual(response.context.get("segment"), "pacientes")


class RegistrarPacienteViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Simular Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_reg@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00000001",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

    def test_registro_paciente_get_usa_template(self):
        response = self.client.get(reverse("registro_paciente"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/registrar_pacientes.html")
        self.assertEqual(response.context.get("segment"), "pacientes")

    def test_registro_paciente_post_valido_crea_entidad_y_rol_paciente(self):
        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Paciente",
            "apellidoMaterno": "Apellido",
            "correo": "nuevo_paciente@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "33333333",
        }

        response = self.client.post(reverse("registro_paciente"), data)

        # Debe redirigir a lista_pacientes
        self.assertRedirects(response, reverse("lista_pacientes"))

        # Se creó la Entidad
        entidad = Entidad.objects.get(dni="33333333")
        self.assertEqual(entidad.correo, "nuevo_paciente@example.com")

        # Se creó/asignó el rol Paciente (por nombre_rol)
        rol_paciente = Rol.objects.get(nombre_rol="Paciente")
        rel = RolEntidad.objects.get(entidad=entidad, rol=rol_paciente)
        self.assertIsNotNone(rel)

    def test_registro_paciente_post_dni_duplicado_muestra_error_y_no_redirige(self):
        # Entidad existente con mismo DNI
        Entidad.objects.create(
            nombre="Existente",
            apellidoPaterno="Uno",
            apellidoMaterno="Apellido",
            correo="existente@example.com",
            contraseña="123456",
            telefono="777777777",
            dni="44444444",
        )

        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Paciente",
            "apellidoMaterno": "Apellido",
            "correo": "nuevo@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "44444444",  # mismo DNI
        }

        response = self.client.post(reverse("registro_paciente"), data)

        # No debe redirigir: se queda en la misma página de registro
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/registrar_pacientes.html")

        errors = response.context.get("errors", {})
        self.assertIn("dni", errors)
        self.assertEqual(errors["dni"], "Este DNI ya está registrado.")

        # Solo debe haber UNA Entidad con ese DNI
        self.assertEqual(Entidad.objects.filter(dni="44444444").count(), 1)


class EditarPacienteViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_edit@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00000002",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        self.paciente = Entidad.objects.create(
            nombre="Paciente",
            apellidoPaterno="Original",
            apellidoMaterno="Apellido",
            correo="paciente@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="55555555",
        )

    def test_editar_paciente_get_usa_template_y_contexto(self):
        url = reverse("editar_paciente", args=[self.paciente.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/editar_paciente.html")
        self.assertEqual(response.context.get("paciente"), self.paciente)
        self.assertEqual(response.context.get("segment"), "pacientes")

    def test_editar_paciente_post_valido_actualiza_y_redirige(self):
        url = reverse("editar_paciente", args=[self.paciente.id])
        data = {
            "nombre": "Paciente Editado",
            "apellidoPaterno": "NuevoAp",
            "apellidoMaterno": "NuevoAm",
            "correo": "editado@example.com",
            "telefono": "111111111",
            "dni": "66666666",  # nuevo DNI
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("lista_pacientes"))

        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nombre, "Paciente Editado")
        self.assertEqual(self.paciente.apellidoPaterno, "NuevoAp")
        self.assertEqual(self.paciente.apellidoMaterno, "NuevoAm")
        self.assertEqual(self.paciente.correo, "editado@example.com")
        self.assertEqual(self.paciente.telefono, "111111111")
        self.assertEqual(self.paciente.dni, "66666666")

    def test_editar_paciente_post_dni_duplicado_no_actualiza_y_muestra_error(self):
        # Otro paciente con DNI que va a causar conflicto
        otro = Entidad.objects.create(
            nombre="Otro",
            apellidoPaterno="Paciente",
            apellidoMaterno="Apellido",
            correo="otro@example.com",
            contraseña="123456",
            telefono="000000000",
            dni="77777777",
        )

        url = reverse("editar_paciente", args=[self.paciente.id])
        data = {
            "nombre": "Intento Editar",
            "apellidoPaterno": "X",
            "apellidoMaterno": "Y",
            "correo": "intentando@example.com",
            "telefono": "222222222",
            "dni": "77777777",  # mismo DNI que 'otro'
        }

        response = self.client.post(url, data)

        # No redirige, se queda en editar
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/editar_paciente.html")

        errors = response.context.get("errors", {})
        self.assertIn("dni", errors)
        self.assertEqual(errors["dni"], "Este DNI ya está registrado.")

        # El paciente original NO debe haber cambiado al DNI duplicado
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.dni, "55555555")


class EliminarPacienteViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Entidad logueada en sesión
        self.entidad_admin = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Sistema",
            apellidoMaterno="Hospital",
            correo="admin_del@example.com",
            contraseña="admin123",
            telefono="999999999",
            dni="00000003",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad_admin.id
        session.save()

        self.paciente = Entidad.objects.create(
            nombre="Paciente",
            apellidoPaterno="Eliminar",
            apellidoMaterno="Apellido",
            correo="eliminar@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="88888888",
        )

    def test_eliminar_paciente_borra_y_redirige(self):
        url = reverse("eliminar_paciente", args=[self.paciente.id])

        # Tu vista usa GET, así que simulamos GET
        response = self.client.get(url)

        # Redirige a lista_pacientes
        self.assertRedirects(response, reverse("lista_pacientes"))

        # El paciente ya no existe
        self.assertFalse(Entidad.objects.filter(id=self.paciente.id).exists())
