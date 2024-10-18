from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('registrarCategoria/', views.registrarCategoria),
    path('edicionCategoria/<int:cod_categoria>/', views.edicionCategoria),
    path('editarCategoria/', views.editarCategoria),
    path('eliminarCategoria/<cod_categoria>', views.eliminarCategoria)
]
