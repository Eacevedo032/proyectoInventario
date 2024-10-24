from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('gestionCategoria/', views.gestionCategorias, name='gestionCategoria'), #añadi nombre
    path('registrarCategoria/', views.registrarCategoria),
    path('edicionCategoria/<str:cod_categoria>/', views.edicionCategoria, name='edicionCategoria'),
    path('editarCategoria/', views.editarCategoria, name='editarCategoria'), #añadi nombre
    path('eliminarCategoria/<cod_categoria>/', views.eliminarCategoria, name='eliminarCategoria'),
    path('accounts/', include('django.contrib.auth.urls'))
]
