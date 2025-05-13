from django.urls import path, include
from aplicaciones.appGestionLaboratorios.views import views
from aplicaciones.appGestionLaboratorios.views.reservar_laboratorio import enviar_solicitud

urlpatterns = [
    # URLs para formulario y tabla de laboratorio
    path('reservar_laboratorio/', views.reservar_laboratorio, name='reservar_laboratorio'),
    path('enviar_solicitud/<int:solicitud_id>/', enviar_solicitud, name='enviar_solicitud'),
    path('editar_laboratorio/<int:solicitud_id>/', views.editar_laboratorio, name='editar_laboratorio'),
    path('eliminar_solicitud/<int:solicitud_id>/', views.eliminar_solicitud, name='eliminar_solicitud'),

    # URLs para formulario y tabla de recursos utilizados en el laboratorio
    path('solicitar_recursos/', views.solicitar_recursos, name='solicitar_recursos'),
    path('editar_recurso/<int:uso_id>/', views.editar_recurso, name='editar_recurso'),
    path('eliminar_recurso/<int:uso_id>/', views.eliminar_recurso, name='eliminar_recurso'),

    #URLS para solicitar productos de inventario
    path('solicitar-productos/', views.solicitar_productos, name='solicitar_productos'),
    path('enviar-productos/<int:producto_id>/', views.enviar_productos, name='enviar_productos'),
    path('editar-productos/<int:producto_id>/', views.editar_productos, name='editar_productos'),
    path('eliminar-productos/<int:producto_id>/', views.eliminar_productos, name='eliminar_productos'),
    
    #Urls para llamar a las categorias a las que pertenece cada recurso de los productos
    path('obtener_subcategorias/<int:categoria_id>/', views.obtener_subcategorias, name='obtener_subcategorias'),
    path('obtener_items/', views.obtener_items, name='obtener_items'),
    
    # URLs para usuarios admin laboratorios
    path('administracionLaboratorios/', views.administracionLaboratorios, name='administracion_laboratorios'),
    path('ver-items-solicitud/<int:solicitud_id>/', views.ver_items_solicitud, name='ver_items_solicitud'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitud_pendiente/<int:solicitud_id>/', views.solicitud_pendiente, name='solicitud_pendiente'),

    # URLs para usuario admin recursos  
    path('administracionRecursos/', views.administracionRecursos, name='administracion_recursos'),
    path('aprobar_solicitud_producto/<int:solicitud_id>/', views.aprobar_solicitud_producto, name='aprobar_solicitud_producto'),
    path('rechazar_solicitud_producto/<int:solicitud_id>/', views.rechazar_solicitud_producto, name='rechazar_solicitud_producto'),
    path('solicitud_pendiente_producto/<int:solicitud_id>/', views.solicitud_pendiente_producto, name='solicitud_pendiente_producto'),

    #Urls para horarios de laboratorio
    path('listar_horarios/', views.listar_horarios, name='listar_horarios'),
    path('editar_horario/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('eliminar_horario/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    path('agregar_horario/', views.agregar_horario, name='agregar_horario'),
    path('listar_horarios_lectura/', views.listar_horarios_lectura, name='listar_horarios_lectura')
]