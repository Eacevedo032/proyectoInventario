from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('registrarCategoria/', views.registrarCategoria),
    path('edicionCategoria/<int:cod_categoria>/', views.edicionCategoria),
    path('editarCategoria/', views.editarCategoria),
    path('eliminarCategoria/<cod_categoria>', views.eliminarCategoria),
    path('accounts/', include('django.contrib.auth.urls'))
]
