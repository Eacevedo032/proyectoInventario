from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('listar/', views.listar_productos, name='listar_productos'),
    path('gestionarCatalogoCategoria/', views.gestionar_catalogos_categoria, name='gestionar_catalogos_categoria'), #Gestionar catálogo de Categrías
    path('ajax/obtener-subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'), #Url de carga de solo subcategorias creadas para X categoria
    path('', views.menu_inventario, name='menu_inventario'),  # Ruta para el menú principal
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
]