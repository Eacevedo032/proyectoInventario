from django.urls import path
from .views import views
from aplicaciones.appReportes.views import views

urlpatterns = [

    #urls de Reportes de laboratorio
    path('listar_reportes/', views.listar_reportes, name='listar_reportes'),
    path('crear_reporte/', views.crear_reporte, name='crear_reporte'),
    path('detalle_reporte/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
]

