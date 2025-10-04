from django.urls import path
from . import views

urlpatterns = [
    path("medicos/registro/", views.registrar_medico, name="registro_medico"),
    path("medicos/lista/", views.lista_medicos, name="lista_medicos"),
    path('medicos/editar/<int:pk>/', views.editar_medico, name='editar_medico'),
    path('medicos/eliminar/<int:pk>/', views.eliminar_medico, name='eliminar_medico'),

    path("pacientes/registro/", views.registrar_paciente, name="registro_paciente"),
    path("pacientes/lista/", views.lista_pacientes, name="lista_pacientes"),
    path("pacientes/editar/<int:pk>/", views.editar_paciente, name="editar_paciente"),
    path("pacientes/eliminar/<int:pk>/", views.eliminar_paciente, name="eliminar_paciente"),

    path("citas/paciente/<int:paciente_id>/lista/", views.lista_citas_paciente, name="lista_citas_paciente"),
    path("citas/paciente/<int:paciente_id>/registrar/", views.registrar_cita_paciente, name="registrar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/editar/<int:pk>/", views.editar_cita_paciente, name="editar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/eliminar/<int:pk>/", views.eliminar_cita_paciente, name="eliminar_cita_paciente"),

    path("citas/doctor/<int:doctor_id>/lista/", views.lista_citas_doctor, name="lista_citas_doctor"),



    path('medicos/horario/registro/', views.registrar_horario_medico, name='registro_horario_medico'),
    path('medicos/horario/lista/', views.lista_horarios_medico, name='lista_horarios_medico'),
    path('horario/editar/<int:pk>/', views.editar_horario_medico, name='editar_horario_medico'),
    path('horario/eliminar/<int:pk>/', views.eliminar_horario_medico, name='eliminar_horario_medico'),

    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),

    path('', views.login_view),
    path('logout/', views.logout_view, name='logout'),

    path('index/', views.index, name='index'),
    path('mantenimiento/', views.mantenimiento_roles_especialidades, name='mantenimiento_roles_especialidades'),
]