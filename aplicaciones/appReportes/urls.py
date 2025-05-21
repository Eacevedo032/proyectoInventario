from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from aplicaciones.appReportes.views import views

urlpatterns = [
    # urls de Reportes de laboratorio
    path('solicitud/<int:solicitud_id>/finalizar/', views.finalizar_uso, name='finalizar_uso'),
    path('listar_reportes/', views.listar_reportes, name='listar_reportes'),
    path('detalle_reporte/<int:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

