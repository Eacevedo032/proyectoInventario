from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('gestionCategorias/', views.gestionCategorias, name='gestionCategoria'),
    path('registrarCategoria/', views.registrarCategoria),
    path('edicionCategoria/<int:id_categoria>/', views.edicionCategoria, name='edicionCategoria'),
    path('eliminarCategoria/<id_categoria>/', views.eliminarCategoria, name='eliminarCategoria'),
    path('accounts/', include('django.contrib.auth.urls'))
]
