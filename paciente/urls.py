from django.urls import path
from . import views

urlpatterns = [
    path("pacientes/registro/", views.registrar_paciente, name="registro_paciente"),
    path("pacientes/lista/", views.lista_pacientes, name="lista_pacientes"),
    path("pacientes/editar/<int:pk>/", views.editar_paciente, name="editar_paciente"),
    path("pacientes/eliminar/<int:pk>/", views.eliminar_paciente, name="eliminar_paciente"),
]