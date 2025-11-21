from django.test import TestCase, Client
from django.urls import reverse

from database.models import Rol, Especialidad, Entidad


class MantenimientoRolesEspecialidadesViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Simulamos una sesión válida
        self.entidad = Entidad.objects.create(
            nombre="Admin",
            apellidoPaterno="Test",
            apellidoMaterno="User",
            correo="admin@test.com",
            contraseña="123456",
            telefono="999999999",
            dni="12345679"
        )

        session = self.client.session
        session["entidad_id"] = self.entidad.id
        session.save()

        self.url = reverse("mantenimiento_roles_especialidades")

        # Datos base
        self.rol = Rol.objects.create(nombre_rol="Doctor")
        self.especialidad = Especialidad.objects.create(nombre="Cardiología")

    # ------------------- GET -------------------

    def test_get_muestra_template_y_listas(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "mantenimiento/mantenimiento_roles_especialidades.html")
        self.assertIn("roles", response.context)
        self.assertIn("especialidades", response.context)

    # ------------------- ROLES -------------------

    def test_post_agregar_rol(self):
        response = self.client.post(self.url, {
            "accion": "agregar_rol",
            "nuevo_rol": "Enfermero"
        })

        self.assertRedirects(response, self.url)
        self.assertTrue(Rol.objects.filter(nombre_rol="Enfermero").exists())

    def test_post_editar_rol(self):
        response = self.client.post(self.url, {
            "accion": "editar_rol",
            "rol_id": self.rol.id,
            "editar_rol": "Doctor especialista"
        })

        self.assertRedirects(response, self.url)
        self.rol.refresh_from_db()
        self.assertEqual(self.rol.nombre_rol, "Doctor especialista")

    def test_post_eliminar_rol(self):
        response = self.client.post(self.url, {
            "accion": "eliminar_rol",
            "rol_id": self.rol.id
        })

        self.assertRedirects(response, self.url)
        self.assertFalse(Rol.objects.filter(id=self.rol.id).exists())

    # ------------------- ESPECIALIDADES -------------------

    def test_post_agregar_especialidad(self):
        response = self.client.post(self.url, {
            "accion": "agregar_especialidad",
            "nueva_especialidad": "Neurología"
        })

        self.assertRedirects(response, self.url)
        self.assertTrue(Especialidad.objects.filter(nombre="Neurología").exists())

    def test_post_editar_especialidad(self):
        response = self.client.post(self.url, {
            "accion": "editar_especialidad",
            "especialidad_id": self.especialidad.id,
            "editar_especialidad": "Cardiología Pediátrica"
        })

        self.assertRedirects(response, self.url)
        self.especialidad.refresh_from_db()
        self.assertEqual(self.especialidad.nombre, "Cardiología Pediátrica")

    def test_post_eliminar_especialidad(self):
        response = self.client.post(self.url, {
            "accion": "eliminar_especialidad",
            "especialidad_id": self.especialidad.id
        })

        self.assertRedirects(response, self.url)
        self.assertFalse(Especialidad.objects.filter(id=self.especialidad.id).exists())
