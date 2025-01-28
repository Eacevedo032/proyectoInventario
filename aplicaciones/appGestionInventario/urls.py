from django.urls import path, include
from aplicaciones.appGestionInventario.views import views
from aplicaciones.appGestionInventario.views import inicio

urlpatterns = [
    path('', views.inicio, name='inicio'),

    #urls para gestiones de categorias 
    path('gestionCategorias/', views.gestionCategorias, name='gestionCategoria'),
    path('registrarCategoria/', views.registrarCategoria, name='registrarCategoria'),
    path('edicionCategoria/<int:id_categoria>/', views.edicionCategoria, name='edicionCategoria'),
    path('eliminarCategoria/<int:id_categoria>/', views.eliminarCategoria, name='eliminarCategoria'),

    #urls para gestiones de subCategorias
    path('gestionSubcategorias/<int:id_categoria>/', views.gestionSubcategorias, name='gestionSubcategorias'),
    path('agregarSubcategoria/<int:id_categoria>/', views.agregarSubcategoria, name='agregarSubcategoria'),
    path('editarSubcategoria/<int:id_subcategoria>/', views.editarSubcategoria, name='editarSubcategoria'),
    path('eliminarSubcategoria/<int:id_subcategoria>/', views.eliminarSubcategoria, name='eliminarSubcategoria'),

    #urls para gestiones de inventario
    path('inventarioGeneral/', views.inventario_general, name='inventario_general'),
    path('verInventarioGeneral/', views.verInventarioGeneral, name='verInventarioGeneral'),
    path("editarInventario/<int:id_inventario>/", views.editarInventario, name="editarInventario"),
    path("eliminarInventario/<int:id_inventario>/", views.eliminarInventario, name="eliminarInventario"),
    path("agregarInventario/<int:id_subcategoria>/", views.agregarInventario, name="agregarInventario"),#URL para agregar Inventario
    #Podría dejar este path ultimo sin parametro (id_subcategoria) cuando se use un formulario genérico donde el usuario seleccione la subcategoría manualmente.

    #urls para las configuraciones de cuentas de usuario
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register_user, name='register'),
    path('approve-users/', views.approve_users, name='approve_users')
]
#La primer parte del path define el URL, la siguiente asocia el URL con la vista, el tercero
# le da un nombre único para reutilizarlo dentro del código
#Esto: <int:id_categoria> Permite pasar un valor dinámico (id_categoria) como argumento