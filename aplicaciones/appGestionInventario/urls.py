from django.urls import path, include
from aplicaciones.appGestionInventario.views import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView
from .views import exportar_inventario_excel, exportar_inventario_pdf
from .views import exportar_inventario_actual_excel, exportar_inventario_actual_pdf
from .views.Usuarios import edit_profile  # Importa la vista desde el archivo Usuarios.py para edición del perfil de usuario


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
    path('guardar_inventario_general/', views.guardar_inventario_general, name='guardar_inventario_general'),
    path('historial_inventario/', views.historial_inventario_general, name='historial_inventario_general'),
    path('historial_inventario/<int:pk>/', views.detalle_inventario_guardado, name='detalle_inventario_guardado'),
    path('eliminar_inventario_guardado/<int:id_guardado>/', views.eliminarInventarioGuardado, name='eliminarInventarioGuardado'),
    path('verInventarioGuardar/', views.verInventarioGuardar, name='verInventarioGuardar'),
    path("agregarInventario/<int:id_subcategoria>/", views.agregarInventario, name="agregarInventario"),#URL para agregar Inventario
    #Podría dejar este path ultimo sin parametro (id_subcategoria) cuando se use un formulario genérico donde el usuario seleccione la subcategoría manualmente.

    #urls para historial del inventario
    path("registrar_cambio_inventario/", views.registrar_cambio_inventario, name="registrar_cambio_inventario"),

    #urls para las configuraciones de cuentas de usuario
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register_user, name='register'),
    path('approve-users/', views.approve_users, name='approve_users'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('editar-perfil/', views.edit_profile, name='editar_perfil'),  # Para editar el perfil
    path('logout/', LogoutView.as_view(), name='logout'),

    #urls para los guardados de inventario
    path('inventario/<int:pk>/exportar/excel/', views.exportar_inventario_excel, name='exportar_inventario_excel'),
    path('inventario/<int:pk>/exportar/pdf/', views.exportar_inventario_pdf, name='exportar_inventario_pdf'),
    path('inventario/exportar/excel/', views.exportar_inventario_actual_excel, name='exportar_inventario_excel'),
    path('inventario/exportar/pdf/', views.exportar_inventario_actual_pdf, name='exportar_inventario_pdf'),
]
#La primer parte del path define el URL, la siguiente asocia el URL con la vista, el tercero
# le da un nombre único para reutilizarlo dentro del código
#Esto: <int:id_categoria> Permite pasar un valor dinámico (id_categoria) como argumento