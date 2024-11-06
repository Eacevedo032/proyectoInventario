from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('gestionCategorias/', views.gestionCategorias, name='gestionCategoria'),
    path('registrarCategoria/', views.registrarCategoria, name='registrarCategoria'),
    path('edicionCategoria/<int:id_categoria>/', views.edicionCategoria, name='edicionCategoria'),
    path('eliminarCategoria/<int:id_categoria>/', views.eliminarCategoria, name='eliminarCategoria'),
    path('gestionSubcategorias/<int:id_categoria>/', views.gestionSubcategorias, name='gestionSubcategorias'),
    path('agregarSubcategoria/<int:id_categoria>/', views.agregarSubcategoria, name='agregarSubcategoria'),
    path('editarSubcategoria/<int:id_subcategoria>/', views.editarSubcategoria, name='editarSubcategoria'),
    path('eliminarSubcategoria/<int:id_subcategoria>/', views.eliminarSubcategoria, name='eliminarSubcategoria'),
    path('verSubcategorias/<int:id_categoria>/', views.verSubcategorias, name='verSubcategorias'),
    path('accounts/', include('django.contrib.auth.urls')),
]
