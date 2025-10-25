from django.urls import path
from . import views

urlpatterns = [
    path('checkin/<int:cita_id>/', views.checkin_view, name='checkin'),
    path('tablero/<int:doctor_id>/', views.tablero_cola, name='tablero_cola'),
    path('cancelar/<int:cita_id>/', views.cancelar_cita_view, name='cancelar_cita'),
    path('waitlist/aceptar/<int:item_id>/<str:token>/', views.aceptar_waitlist_token_view, name='aceptar_waitlist_token'),
    path('waitlist/aceptar/<int:item_id>/', views.aceptar_waitlist_view, name='aceptar_waitlist'),
    path("citas/paciente/<int:paciente_id>/lista/", views.lista_citas_paciente, name="lista_citas_paciente"),
    path("citas/paciente/<int:paciente_id>/registrar/", views.registrar_cita_paciente, name="registrar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/editar/<int:pk>/", views.editar_cita_paciente, name="editar_cita_paciente"),
    path("citas/paciente/<int:paciente_id>/eliminar/<int:pk>/", views.eliminar_cita_paciente, name="eliminar_cita_paciente"),
    path("citas/doctor/<int:doctor_id>/lista/", views.lista_citas_doctor, name="lista_citas_doctor"),
    path('index/', views.index, name='index')
]