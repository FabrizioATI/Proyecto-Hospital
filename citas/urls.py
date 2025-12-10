from django.urls import path
from . import views

urlpatterns = [
    path('cancelar/<int:cita_id>/', views.cancelar_cita_view, name='cancelar_cita'),
    path("citas/paciente/<int:paciente_id>/lista/", views.lista_citas_paciente, name="lista_citas_paciente"),
    path("citas/paciente/<int:paciente_id>/registrar/", views.registrar_cita_paciente, name="registrar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/editar/<int:pk>/", views.editar_cita_paciente, name="editar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/eliminar/<int:pk>/", views.eliminar_cita_paciente, name="eliminar_cita_paciente"),
    path("citas/doctor/<int:doctor_id>/lista/", views.lista_citas_doctor, name="lista_citas_doctor"),
    path('atendida/<int:cita_id>/', views.marcar_cita_atendida, name='marcar_cita_atendida'),
    path('checkin/<int:cita_id>/', views.checkin_view, name='checkin'),
    path("ehr/historias/", views.lista_historias_clinicas, name="lista_historias_clinicas"),
    path("ehr/historias/<int:historia_id>/", views.detalle_historia_clinica, name="detalle_historia_clinica"),
    path('index/', views.index, name='index'),
    path("exportar-agenda-hoy/", views.exportar_agenda_hoy, name="exportar_agenda_hoy")
]