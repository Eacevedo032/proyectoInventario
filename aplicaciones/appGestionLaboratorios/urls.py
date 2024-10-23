from django.urls import path, include
from . import views

urlpatterns = [ 
    path('gestionLaboratorios/', views.gestionLaboratorios, name='gestion_laboratorios'),
    path('administracionLaboratorios/', views.administracionLaboratorios, name='administracion_laboratorios')
]