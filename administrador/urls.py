from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('mantenimiento/', views.mantenimiento_roles_especialidades, name='mantenimiento_roles_especialidades'),

    # Vista de menú de reportes
    path('reportes/', views.vista_reportes, name='vista_reportes'),
    
    # Reportes Excel básicos
    path('reportes/roles/', views.export_roles_excel, name='export_roles_excel'),
    path('reportes/especialidades/', views.export_especialidades_excel, name='export_especialidades_excel'),
    path('reportes/citas/', views.export_citas_excel, name='export_citas_excel'),

    # Reportes Excel analíticos
    path('reportes/citas-estado/', views.export_citas_por_estado_excel, name='export_citas_por_estado_excel'),
    path('reportes/citas-especialidad/', views.export_citas_por_especialidad_excel, name='export_citas_por_especialidad_excel'),
    path('reportes/noshow-doctor/', views.export_noshow_por_doctor_excel, name='export_noshow_por_doctor_excel'),
    path('reportes/cancelaciones-paciente/', views.export_cancelaciones_por_paciente_excel, name='export_cancelaciones_por_paciente_excel'),
    path('reportes/waitlist-resumen/', views.export_waitlist_resumen_excel, name='export_waitlist_resumen_excel'),
]
