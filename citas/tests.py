from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from database.models import (
    Entidad,
    Especialidad,
    DoctorDetalle,
    Horario,
    DoctorHorario,
    Cita,
)


class BaseCitasTestCase(TestCase):
    def setUp(self):
        # Paciente
        self.paciente = Entidad.objects.create(
            nombre="Juan",
            apellidoPaterno="Pérez",
            apellidoMaterno="Gómez",
            correo="juan@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="12345678",
        )

        # Otro paciente
        self.otro_paciente = Entidad.objects.create(
            nombre="Ana",
            apellidoPaterno="Ramos",
            apellidoMaterno="Lopez",
            correo="ana@example.com",
            contraseña="123456",
            telefono="988888888",
            dni="87654321",
        )

        # Especialidad
        self.especialidad = Especialidad.objects.create(nombre="Cardiología")

        # Doctor (Entidad + DoctorDetalle)
        self.doctor_entidad = Entidad.objects.create(
            nombre="Dr. Luis",
            apellidoPaterno="Médico",
            apellidoMaterno="Apellido",
            correo="doc@example.com",
            contraseña="123456",
            telefono="977777777",
            dni="11223344",
        )
        self.doctor = DoctorDetalle.objects.create(
            entidad=self.doctor_entidad,
            especialidad=self.especialidad,
            nro_colegiatura="COL-001",
        )

        # Horario y DoctorHorario
        self.horario = Horario.objects.create(
            fecha=date(2025, 1, 10),
            hora_inicio=time(9, 0),
            hora_fin=time(9, 30),
        )
        self.doctor_horario = DoctorHorario.objects.create(
            doctor=self.doctor,
            horario=self.horario,
        )

        # Cita principal (ligada al paciente 1)
        self.cita = Cita.objects.create(
            paciente=self.paciente,
            doctor_horario=self.doctor_horario,
            doctor=self.doctor_entidad,  # Entidad, no DoctorDetalle
            motivo="Dolor de cabeza",
            tipo_cita="PRESENCIAL",
            estado="pendiente",
        )

        # Otra cita para otro paciente (para probar filtrado)
        self.cita_otro_paciente = Cita.objects.create(
            paciente=self.otro_paciente,
            doctor_horario=self.doctor_horario,
            doctor=self.doctor_entidad,
            motivo="Chequeo general",
            tipo_cita="PRESENCIAL",
            estado="pendiente",
        )


class ListaCitasPacienteViewTests(BaseCitasTestCase):
    def test_lista_citas_paciente_redirige_a_login_si_no_autenticado(self):
        url = reverse("lista_citas_paciente", args=[self.paciente.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class RegistrarCitaPacienteViewTests(BaseCitasTestCase):
    def test_registro_cita_get_redirige_a_login_si_no_autenticado(self):
        url = reverse("registrar_cita_paciente", args=[self.paciente.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_registro_cita_post_sin_doctor_redirige_a_login(self):
        url = reverse("registrar_cita_paciente", args=[self.paciente.id])
        data = {
            "doctor_id": "",
            "clasificacion": "REGULAR",
            "tipo_cita": "PRESENCIAL",
            "motivo": "Motivo cualquiera",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_registro_cita_post_sin_motivo_redirige_a_login(self):
        url = reverse("registrar_cita_paciente", args=[self.paciente.id])
        data = {
            "doctor_id": self.doctor.id,
            "clasificacion": "REGULAR",
            "tipo_cita": "PRESENCIAL",
            "motivo": "",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    @patch("citas.views.solicitar_cita")
    def test_registro_cita_post_valido_redirige_a_login_y_no_llama_servicio(self, mock_solicitar):
        url = reverse("registrar_cita_paciente", args=[self.paciente.id])
        data = {
            "doctor_id": self.doctor.id,
            "clasificacion": "REGULAR",
            "tipo_cita": "PRESENCIAL",
            "motivo": "Necesito una cita",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
        mock_solicitar.assert_not_called()


class EditarCitaPacienteViewTests(BaseCitasTestCase):
    def test_editar_cita_get_redirige_a_login_si_no_autenticado(self):
        url = reverse("editar_cita_paciente", args=[self.paciente.id, self.cita.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_editar_cita_post_valido_redirige_a_login(self):
        url = reverse("editar_cita_paciente", args=[self.paciente.id, self.cita.id])
        data = {
            "motivo": "Motivo actualizado",
            "tipo_cita": "VIRTUAL",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_editar_cita_post_sin_motivo_redirige_a_login(self):
        url = reverse("editar_cita_paciente", args=[self.paciente.id, self.cita.id])
        data = {
            "motivo": "",
            "tipo_cita": "PRESENCIAL",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_editar_cita_post_tipo_invalido_redirige_a_login(self):
        url = reverse("editar_cita_paciente", args=[self.paciente.id, self.cita.id])
        data = {
            "motivo": "Algo",
            "tipo_cita": "OTRO",  # no válido
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class EliminarCitaPacienteViewTests(BaseCitasTestCase):
    def test_eliminar_cita_redirige_a_login_si_no_autenticado(self):
        url = reverse("eliminar_cita_paciente", args=[self.paciente.id, self.cita.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class ListaCitasDoctorViewTests(BaseCitasTestCase):
    def test_lista_citas_doctor_redirige_a_login_si_no_autenticado(self):
        url = reverse("lista_citas_doctor", args=[self.doctor_entidad.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CancelarCitaViewTests(BaseCitasTestCase):
    @patch("citas.views.services.cancelar_y_ofertar")
    def test_cancelar_cita_redirige_a_login_y_no_llama_servicio(self, mock_cancelar):
        url = reverse("cancelar_cita", args=[self.cita.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
        mock_cancelar.assert_not_called()
