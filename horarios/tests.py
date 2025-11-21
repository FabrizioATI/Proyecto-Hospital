from datetime import datetime, date, time, timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from database.models import (
    Entidad,
    DoctorDetalle,
    Horario,
    DoctorHorario,
    Holiday,
    Especialidad,
)


class HolidaysJsonViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Simular "login" como en el resto del sistema:
        # crear una Entidad y guardar su id en la sesión
        self.entidad = Entidad.objects.create(
            nombre="Usuario",
            apellidoPaterno="Prueba",
            apellidoMaterno="Holidays",
            correo="holidays@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="90909090",
        )
        session = self.client.session
        session["entidad_id"] = self.entidad.id
        session.save()

    def test_holidays_json_devuelve_lista_iso(self):
        today = timezone.localdate()
        h1, _ = Holiday.objects.get_or_create(fecha=today)
        h2, _ = Holiday.objects.get_or_create(fecha=today + timedelta(days=1))

        response = self.client.get(reverse("holidays_json"))

        # ahora sí debe ser 200, no 302
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn(h1.fecha.isoformat(), data)
        self.assertIn(h2.fecha.isoformat(), data)

class ListaHorariosMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.especialidad = Especialidad.objects.create(nombre="Cardiología")

        self.entidad_doc = Entidad.objects.create(
            nombre="DocSesion",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="doc_sesion@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="10101010",
        )
        self.doctor_sesion = DoctorDetalle.objects.create(
            entidad=self.entidad_doc,
            especialidad=self.especialidad,
            nro_colegiatura="COL-SESION",
        )

        session = self.client.session
        session["entidad_id"] = self.entidad_doc.id
        session.save()

        entidad_otro = Entidad.objects.create(
            nombre="DocOtro",
            apellidoPaterno="Tres",
            apellidoMaterno="Cuatro",
            correo="doc_otro@example.com",
            contraseña="123456",
            telefono="888888888",
            dni="20202020",
        )
        self.doctor_otro = DoctorDetalle.objects.create(
            entidad=entidad_otro,
            especialidad=self.especialidad,
            nro_colegiatura="COL-OTRO",
        )

        fecha = timezone.localdate() + timedelta(days=1)
        h1 = Horario.objects.create(
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(8, 30),
        )
        h2 = Horario.objects.create(
            fecha=fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(9, 30),
        )
        self.dh_sesion = DoctorHorario.objects.create(
            doctor=self.doctor_sesion,
            horario=h1,
        )
        self.dh_otro = DoctorHorario.objects.create(
            doctor=self.doctor_otro,
            horario=h2,
        )

    def test_lista_horarios_medico_usa_template_y_filtra_por_doctor_sesion(self):
        response = self.client.get(reverse("lista_horarios_medico"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "doctor_horario/lista_horario_medicos.html"
        )

        horarios = response.context["horarios"]
        self.assertIn(self.dh_sesion, horarios)
        self.assertNotIn(self.dh_otro, horarios)

        doctor_sesion_ctx = response.context.get("doctor_sesion")
        self.assertEqual(doctor_sesion_ctx, self.doctor_sesion)


class RegistrarHorarioMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.especialidad = Especialidad.objects.create(nombre="Pediatría")

        self.entidad_doc = Entidad.objects.create(
            nombre="DocSesion",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="doc_sesion@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="30303030",
        )
        self.doctor_sesion = DoctorDetalle.objects.create(
            entidad=self.entidad_doc,
            especialidad=self.especialidad,
            nro_colegiatura="COL-REG",
        )

        session = self.client.session
        session["entidad_id"] = self.entidad_doc.id
        session.save()

    def test_registro_horario_get_usa_template_y_contexto(self):
        response = self.client.get(reverse("registro_horario_medico"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "doctor_horario/registrar_horario_medicos.html"
        )

        self.assertEqual(response.context.get("doctor_sesion"), self.doctor_sesion)
        self.assertIn("time_slots", response.context)
        self.assertIn("hoy", response.context)

    def test_registro_horario_post_valido_crea_slots_de_30_min_y_redirige(self):
        fecha = timezone.localdate() + timedelta(days=1)
        fecha_str = fecha.strftime("%Y-%m-%d")

        data = {
            "fecha": fecha_str,
            "hora_inicio": "08:00",
            "hora_fin": "09:00",
        }

        response = self.client.post(
            reverse("registro_horario_medico"), data
        )

        self.assertRedirects(response, reverse("lista_horarios_medico"))

        dhs = DoctorHorario.objects.filter(
            doctor=self.doctor_sesion,
            horario__fecha=fecha,
        )
        self.assertEqual(dhs.count(), 2)

        horas = sorted(
            (dh.horario.hora_inicio.strftime("%H:%M"), dh.horario.hora_fin.strftime("%H:%M"))
            for dh in dhs
        )
        self.assertEqual(
            horas,
            [("08:00", "08:30"), ("08:30", "09:00")],
        )

    def test_registro_horario_con_fecha_pasada_muestra_error(self):
        fecha = timezone.localdate() - timedelta(days=1)
        fecha_str = fecha.strftime("%Y-%m-%d")

        data = {
            "fecha": fecha_str,
            "hora_inicio": "08:00",
            "hora_fin": "09:00",
        }

        response = self.client.post(
            reverse("registro_horario_medico"), data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "doctor_horario/registrar_horario_medicos.html"
        )

        errors = response.context.get("errors", {})
        self.assertIn("fecha", errors)
        self.assertIn("No puedes registrar horarios en una fecha pasada", errors["fecha"])


class EditarHorarioMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.especialidad1 = Especialidad.objects.create(nombre="Neurología")
        self.especialidad2 = Especialidad.objects.create(nombre="Dermatología")

        self.entidad_doc = Entidad.objects.create(
            nombre="DocSesion",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="doc_sesion_hor_edit@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="40404040",
        )
        self.doctor_sesion = DoctorDetalle.objects.create(
            entidad=self.entidad_doc,
            especialidad=self.especialidad1,
            nro_colegiatura="COL-EDIT1",
        )

        self.entidad_otro = Entidad.objects.create(
            nombre="DocOtro",
            apellidoPaterno="X",
            apellidoMaterno="Y",
            correo="doc_otro_hor_edit@example.com",
            contraseña="123456",
            telefono="888888888",
            dni="50505050",
        )
        self.doctor_otro = DoctorDetalle.objects.create(
            entidad=self.entidad_otro,
            especialidad=self.especialidad2,
            nro_colegiatura="COL-EDIT2",
        )

        session = self.client.session
        session["entidad_id"] = self.entidad_doc.id
        session.save()

        self.fecha = timezone.localdate() + timedelta(days=2)
        self.horario = Horario.objects.create(
            fecha=self.fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(10, 30),
        )
        self.doctor_horario = DoctorHorario.objects.create(
            doctor=self.doctor_sesion,
            horario=self.horario,
        )

    def test_editar_horario_get_usa_template_y_contexto(self):
        url = reverse("editar_horario_medico", args=[self.doctor_horario.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "doctor_horario/editar_horario_medico.html"
        )

        self.assertEqual(response.context.get("doctor_horario"), self.doctor_horario)
        doctores = response.context.get("doctores")
        self.assertIn(self.doctor_sesion, doctores)
        self.assertIn(self.doctor_otro, doctores)
        self.assertIn("time_slots", response.context)

    def test_editar_horario_post_valido_actualiza_y_redirige(self):
        url = reverse("editar_horario_medico", args=[self.doctor_horario.id])
        nueva_fecha = self.fecha + timedelta(days=1)
        data = {
            "doctor": str(self.doctor_otro.id),
            "fecha": nueva_fecha.strftime("%Y-%m-%d"),
            "hora_inicio": "11:00",
            "hora_fin": "11:30",
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse("lista_horarios_medico"))

        self.doctor_horario.refresh_from_db()
        self.horario.refresh_from_db()

        self.assertEqual(self.doctor_horario.doctor, self.doctor_otro)
        self.assertEqual(self.horario.fecha, nueva_fecha)
        self.assertEqual(self.horario.hora_inicio.strftime("%H:%M"), "11:00")
        self.assertEqual(self.horario.hora_fin.strftime("%H:%M"), "11:30")

    def test_editar_horario_post_en_conflicto_muestra_error(self):
        # Creamos un horario que se solape con lo que intentaremos guardar
        conflicto_horario = Horario.objects.create(
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )
        DoctorHorario.objects.create(
            doctor=self.doctor_sesion,
            horario=conflicto_horario,
        )

        url = reverse("editar_horario_medico", args=[self.doctor_horario.id])

        # Usamos horas válidas (múltiplos de 30) pero que se SOLAPEN con 09:00–10:00
        data = {
            "doctor": str(self.doctor_sesion.id),
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "hora_inicio": "09:30",
            "hora_fin": "10:00",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "doctor_horario/editar_horario_medico.html"
        )

        errors = response.context.get("errors", {})
        self.assertIn("conflictos", errors)
        self.assertIn("solapa", errors["conflictos"])

        self.doctor_horario.refresh_from_db()
        self.horario.refresh_from_db()
        self.assertEqual(self.horario.hora_inicio.strftime("%H:%M"), "10:00")
        self.assertEqual(self.horario.hora_fin.strftime("%H:%M"), "10:30")


class EliminarHorarioMedicoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.especialidad = Especialidad.objects.create(nombre="Oncología")

        self.entidad_doc = Entidad.objects.create(
            nombre="DocSesion",
            apellidoPaterno="Uno",
            apellidoMaterno="Dos",
            correo="doc_sesion_hor_del@example.com",
            contraseña="123456",
            telefono="999999999",
            dni="60606060",
        )
        self.doctor_sesion = DoctorDetalle.objects.create(
            entidad=self.entidad_doc,
            especialidad=self.especialidad,
            nro_colegiatura="COL-DEL-HOR",
        )

        session = self.client.session
        session["entidad_id"] = self.entidad_doc.id
        session.save()

        fecha = timezone.localdate() + timedelta(days=3)
        self.horario = Horario.objects.create(
            fecha=fecha,
            hora_inicio=time(8, 0),
            hora_fin=time(8, 30),
        )
        self.doctor_horario = DoctorHorario.objects.create(
            doctor=self.doctor_sesion,
            horario=self.horario,
        )

    def test_eliminar_horario_medico_redirige_a_lista(self):
        url = reverse("eliminar_horario_medico", args=[self.doctor_horario.id])
        response = self.client.get(url)

        self.assertRedirects(response, reverse("lista_horarios_medico"))
