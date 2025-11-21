from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('mantenimiento/', views.mantenimiento_roles_especialidades, name='mantenimiento_roles_especialidades'),
]