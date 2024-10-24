from django.urls import path, include
from . import views

urlpatterns = [ 
    path('reservar_laboratorio/', views.reservar_laboratorio, name='reservar_laboratorio'),
    path('administracionLaboratorios/', views.administracionLaboratorios, name='administracion_laboratorios'),
    
    path('mis_solicitudes/', views.lista_solicitudes_usuario, name='lista_solicitudes_usuario'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitud_pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),
]