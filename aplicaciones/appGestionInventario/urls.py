from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('registrarCategoria/', views.registrarCategoria, name='registrarCategoria'),
    path('edicionCategoria/<str:cod_categoria>/', views.edicionCategoria, name='edicionCategoria'),
    path('editarCategoria/', views.editarCategoria, name='editarCategoria'),
    path('eliminarCategoria/<str:cod_categoria>/', views.eliminarCategoria, name='eliminarCategoria'),
    path('accounts/', include('django.contrib.auth.urls'))
]
