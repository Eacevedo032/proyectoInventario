from django.urls import path
from . import views

urlpatterns = [
    path('listar_reportes/', views.listar_reportes, name='listar_reportes'),
    path('crear_reporte/', views.crear_reporte, name='crear_reporte'),
    path('detalle_reporte/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
]

