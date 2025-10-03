from django.urls import path
from . import views

urlpatterns = [
    path("medicos/registro/", views.registrar_medico, name="registro_medico"),
    path("medicos/lista/", views.lista_medicos, name="lista_medicos"),
    path('medicos/editar/<int:pk>/', views.editar_medico, name='editar_medico'),
    path('medicos/eliminar/<int:pk>/', views.eliminar_medico, name='eliminar_medico'),
    path('medicos/horario/<int:pk>/', views.registrarHorarioMedico, name='registro_horariomedico'),
    path('login', views.login, name='login'),
    path('', views.login, name='login'),
    path('register', views.register, name='register'),
]