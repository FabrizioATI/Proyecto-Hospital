from django.urls import path
from . import views

urlpatterns = [
    path('medicos/horario/registro/', views.registrar_horario_medico, name='registro_horario_medico'),
    path('medicos/horario/lista/', views.lista_horarios_medico, name='lista_horarios_medico'),
    path('horario/editar/<int:pk>/', views.editar_horario_medico, name='editar_horario_medico'),
    path('horario/eliminar/<int:pk>/', views.eliminar_horario_medico, name='eliminar_horario_medico'),
    path('index/', views.index, name='index'),
]