from django.urls import path, include
from aplicaciones.appGestionLaboratorios.views import views

urlpatterns = [
    # URLs para formulario y tabla de laboratorio
    path('reservar_laboratorio/', views.reservar_laboratorio, name='reservar_laboratorio'),
     path('eliminar_solicitud/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),

    # URLs para formulario y tabla de recursos
    path('solicitar_recursos/', views.solicitar_recursos, name='solicitar_recursos'),
    
    #Urls para llamar a las categorias a las que pertenece cada recurso del inventario
    path('obtener_subcategorias/<int:categoria_id>/', views.obtener_subcategorias, name='obtener_subcategorias'),
    path('obtener_items/<int:categoria_id>/<int:subcategoria_id>/', views.obtener_items, name='obtener_items'),

    # URLs para usuarios admin
    path('administracionLaboratorios/', views.administracionLaboratorios, name='administracion_laboratorios'),
    path('ver-items-solicitud/<int:solicitud_id>/', views.ver_items_solicitud, name='ver_items_solicitud'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitud_pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),

    #Urls para horarios de laboratorio
    path('listar_horarios/', views.listar_horarios, name='listar_horarios'),
    path('editar_horario/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('eliminar_horario/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    path('agregar_horario/', views.agregar_horario, name='agregar_horario'),
    path('listar_horarios_lectura/', views.listar_horarios_lectura, name='listar_horarios_lectura')
]