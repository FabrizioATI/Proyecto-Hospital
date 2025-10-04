from django.urls import path
from . import views

urlpatterns = [
    path("medicos/registro/", views.registrar_medico, name="registro_medico"),
    path("medicos/lista/", views.lista_medicos, name="lista_medicos"),
    path('medicos/editar/<int:pk>/', views.editar_medico, name='editar_medico'),
    path('medicos/eliminar/<int:pk>/', views.eliminar_medico, name='eliminar_medico'),
    path('medicos/horario/<int:pk>/', views.registrarHorarioMedico, name='horario_medicos'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('', views.login_view),
    path('logout/', views.logout_view, name='logout'),
    path("pacientes/registro/", views.registrar_paciente, name="registro_paciente"),
    path("pacientes/lista/", views.lista_pacientes, name="lista_pacientes"),
    path("pacientes/editar/<int:pk>/", views.editar_paciente, name="editar_paciente"),
    path("pacientes/eliminar/<int:pk>/", views.eliminar_paciente, name="eliminar_paciente"),
]