from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages

from database.models import Entidad, Rol, RolEntidad


class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.entidad = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Pérez",
            apellidoMaterno="García",
            correo="juan@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="12345678",
        )

    def test_index_sin_sesion_redirige_a_login(self):
        response = self.client.get(reverse("index"))

        expected_url = f"{reverse('login')}?next={reverse('index')}"
        self.assertRedirects(response, expected_url)

    def test_index_con_sesion_muestra_template(self):
        # Simular usuario logueado por sesión
        session = self.client.session
        session["entidad_id"] = self.entidad.id
        session["entidad_nombre"] = (
            f"{self.entidad.nombre} {self.entidad.apellidoPaterno} {self.entidad.apellidoMaterno}"
        )
        session.save()

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "123456"

        self.entidad = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Pérez",
            apellidoMaterno="García",
            correo="juan@example.com",
            contraseña=self.password,
            telefono="999999999",
            dni="12345678",
        )

        self.rol_doctor = Rol.objects.create(
            codigo_rol="001",
            nombre_rol="Doctor",
        )
        RolEntidad.objects.create(entidad=self.entidad, rol=self.rol_doctor)

    def test_login_get_muestra_template(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_post_correcto_guarda_sesion_y_redirige_a_index(self):
        response = self.client.post(
            reverse("login"),
            {
                "dni": self.entidad.dni,
                "contraseña": self.password,
            },
        )
        self.assertRedirects(response, reverse("index"))

        session = self.client.session
        self.assertEqual(session.get("entidad_id"), self.entidad.id)
        self.assertEqual(session.get("codigo_rol"), "001")
        self.assertIn("entidad_nombre", session)

    def test_login_post_contrasena_incorrecta_muestra_mensaje_error(self):
        response = self.client.post(
            reverse("login"),
            {
                "dni": self.entidad.dni,
                "contraseña": "mala",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Contraseña no es correct" in m.message for m in messages)
        )

    def test_login_post_usuario_no_encontrado(self):
        response = self.client.post(
            reverse("login"),
            {
                "dni": "99999999",
                "contraseña": "cualquiera",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Usuario no encontrado" in m.message for m in messages)
        )

    def test_login_sin_rol_asignado_muestra_advertencia(self):
        entidad_sin_rol = Entidad.objects.create(
            nombre="Ana",
            apellidoPaterno="Lopez",
            apellidoMaterno="Ramos",
            correo="ana@example.com",
            contraseña="abc123",
            telefono="111111111",
            dni="87654321",
        )

        response = self.client.post(
            reverse("login"),
            {
                "dni": entidad_sin_rol.dni,
                "contraseña": "abc123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("No tienes un rol asignado" in m.message for m in messages)
        )

    def test_root_url_sin_nombre_usa_login_view(self):
        # La ruta '' en urls apunta a login_view
        response = self.client.get("/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.entidad = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Pérez",
            apellidoMaterno="García",
            correo="juan@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="12345678",
        )

    def test_home_con_sesion_entidad_muestra_template_doctor(self):
        session = self.client.session
        session["entidad_id"] = self.entidad.id
        session.save()

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/lista_medicos.html")
        self.assertEqual(response.context["entidad"], self.entidad)

    def test_home_sin_sesion_redirige_a_login(self):
        response = self.client.get(reverse("home"))

        expected_url = f"{reverse('login')}?next={reverse('home')}"
        self.assertRedirects(response, expected_url)

class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.entidad = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Pérez",
            apellidoMaterno="García",
            correo="juan@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="12345678",
        )

    def test_logout_elimina_sesion_y_redirige_a_login(self):
        # Simulamos sesión activa
        session = self.client.session
        session["entidad_id"] = self.entidad.id
        session["codigo_rol"] = "001"
        session.save()

        response = self.client.get(reverse("logout"), follow=True)

        session = self.client.session
        self.assertIsNone(session.get("entidad_id"))
        self.assertIsNone(session.get("codigo_rol"))

        self.assertRedirects(response, reverse("login"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Sesión cerrada correctamente" in m.message for m in messages)
        )


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get_muestra_template(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_post_valido_crea_entidad_y_rol_paciente(self):
        data = {
            "nombre": "Juan",
            "apellidoPaterno": "Pérez",
            "apellidoMaterno": "García",
            "correo": "nuevo@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "12345678",
        }

        response = self.client.post(reverse("register"), data, follow=True)

        self.assertRedirects(response, reverse("login"))

        entidad = Entidad.objects.get(dni="12345678")
        self.assertEqual(entidad.correo, "nuevo@example.com")

        rol_paciente = Rol.objects.get(codigo_rol="002")
        rol_entidad = RolEntidad.objects.get(entidad=entidad, rol=rol_paciente)
        self.assertIsNotNone(rol_entidad)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Cuenta creada con éxito" in m.message for m in messages)
        )

    def test_register_dni_duplicado_muestra_error(self):
        Entidad.objects.create(
            nombre="Existente",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="existente@example.com",
            contraseña="123",
            telefono="000",
            dni="99999999",
        )

        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Pérez",
            "apellidoMaterno": "García",
            "correo": "nuevo@example.com",
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "99999999",  # mismo DNI
        }

        response = self.client.post(reverse("register"), data, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Este DNI ya está registrado" in m.message for m in messages)
        )

    def test_register_correo_duplicado_muestra_error(self):
        Entidad.objects.create(
            nombre="Existente",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="repetido@example.com",
            contraseña="123",
            telefono="000",
            dni="99999999",
        )

        data = {
            "nombre": "Nuevo",
            "apellidoPaterno": "Pérez",
            "apellidoMaterno": "García",
            "correo": "repetido@example.com",  # mismo correo
            "contraseña": "123456",
            "telefono": "999999999",
            "dni": "12345678",
        }

        response = self.client.post(reverse("register"), data, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Este correo ya está registrado" in m.message for m in messages)
        )
