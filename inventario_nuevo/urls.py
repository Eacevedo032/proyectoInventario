from django.urls import path
from inventario_nuevo import views

urlpatterns = [
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('listar/', views.listar_productos, name='listar_productos'),
    path('gestionarCatalogoCategoria/', views.gestionar_catalogos_categoria, name='gestionar_catalogos_categoria'), #Gestionar catálogo de Categrías
    path('ajax/obtener-subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'), #Url de carga de solo subcategorias creadas para X categoria
    path('inventario/menu-catalogos/', views.menu_catalogos, name='menu_catalogos'), #Menu de los Catálogos
    path('catalogos/marcas/', views.gestionar_marca, name='gestionar_marca'),
    path('catalogos/modelos/', views.gestionar_modelo, name='gestionar_modelo'),
    path('catalogos/colores/', views.gestionar_color, name='gestionar_color'),
    path('presentacion/', views.gestionar_presentacion, name='gestionar_presentacion'),
    path('capacidad/', views.gestionar_capacidad, name='gestionar_capacidad'),
    path('accesorios/', views.gestionar_accesorios, name='gestionar_accesorios'),
    path('gestionar-ubicacion/', views.gestionar_ubicacion, name='gestionar_ubicacion'),
    path('gestionar-lote/', views.gestionar_lote, name='gestionar_lote'), #url del catálogo de Lote
    path('gestionar-medida/', views.gestionar_medida, name='gestionar_medida'),
    path('filtrar_por_estados/', views.filtrar_por_estados, name='filtrar_por_estado'), #Url del filtro por estado de un Producto
    path('filtrar_por_unidades/', views.filtrar_por_unidades, name='filtrar_por_unidad'), #Url del filtro por estado de un Producto
    #Para editar el producto
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    #Para dar de baja a un producto
    path('dar_baja_producto/<int:producto_id>/', views.dar_baja_producto, name='dar_baja_producto'),
    #Vista para los reportes del inventario
    path('reportes_inventario/', views.vista_reporte_inventario, name='vista_reporte_inventario'),
    #Exporte del inventario general en PDF
    path('reporte_pdf_inventario/', views.reporte_pdf_inventario, name='reporte_pdf_inventario'),
    #Exporte del inventario general en Excel
    path('reporte_excel_inventario/', views.reporte_excel_inventario, name='reporte_excel_inventario'),
    #Para el acta de bajas


    path('transferencia_producto/', views.transferencia_producto, name='transferencia_producto'),
    path('historial-transferencias/', views.historial_transferencias, name='historial_transferencias'),

    path('registrar-inventario/', views.registrar_inventario_fisico, name='registrar_inventario'),
    path('inventarios-pendientes/', views.lista_inventarios_pendientes, name='lista_inventarios_pendientes'),
    path('inventario/<int:inventario_id>/', views.ver_detalle_inventario, name='ver_detalle_inventario'),  # Sólo si la tienes definida
    path('inventario/<int:inventario_id>/editar/', views.editar_inventario_pendiente, name='editar_inventario_pendiente'),  
    path('inventario/<int:inventario_id>/ejecutar/', views.ejecutar_inventario_fisico, name='ejecutar_inventario'),
    path('cancelar-conteo/', views.cancelar_conteo, name='cancelar_conteo'),
    path('inventarioNuevo/ejecutar-todo/', views.ejecutar_todo_inventario_fisico, name='ejecutar_todo_inventario'),
    path('eliminar-detalle/<int:detalle_id>/', views.eliminar_inventario_pendiente, name='eliminar_inventario_pendiente'),

    path('historial-inventario-fisico/', views.historial_inventario_fisico, name='historial_inventario_fisico'),
    path('exportar-historial-pdf/', views.exportar_historial_pdf, name='exportar_historial_pdf'),
   
]