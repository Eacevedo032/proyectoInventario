from urllib.parse import urljoin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from aplicaciones.appGestionInventario.models import ReporteUsoLaboratorio, SolicitudLaboratorio

def crear_reporte(request):
    """Vista para crear un nuevo reporte vinculado a una solicitud aprobada."""
    solicitudes_aprobadas = SolicitudLaboratorio.objects.filter(estado='aprobada')

    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        numero_estudiantes = request.POST.get('numero_estudiantes')
        objetivo_practica = request.POST.get('objetivo_practica')
        foto = request.FILES.get('foto')

        # Validaciones de datos
        if not solicitud_id:
            messages.error(request, "Debes seleccionar una solicitud.")
        elif not numero_estudiantes or not numero_estudiantes.isdigit():
            messages.error(request, "Debes ingresar un número válido de estudiantes.")
        elif not objetivo_practica:
            messages.error(request, "Debes ingresar el objetivo de la práctica.")
        else:
            try:
                solicitud = SolicitudLaboratorio.objects.get(id=solicitud_id)
                ReporteUsoLaboratorio.objects.create(
                    solicitud=solicitud,
                    numero_estudiantes=int(numero_estudiantes),
                    objetivo_practica=objetivo_practica,
                    foto=foto
                )
                messages.success(request, "Reporte creado exitosamente.")
                return redirect('listar_reportes')
            except SolicitudLaboratorio.DoesNotExist:
                messages.error(request, "La solicitud seleccionada no existe.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error: {e}")

    return render(request, 'crear_reporte.html', {'solicitudes': solicitudes_aprobadas})

def detalle_reporte(request, reporte_id):
    """Vista para ver el detalle de un reporte específico."""
    reporte = get_object_or_404(ReporteUsoLaboratorio, id=reporte_id)

    laboratorio_nombre = reporte.solicitud.laboratorio

    # Generar la URL completa de la imagen si existe
    foto_url = None
    if reporte.foto:
        foto_url = urljoin(settings.MEDIA_URL, reporte.foto.name)

    return render(request, 'detalle_reporte.html', {'reporte': reporte, 'foto_url': foto_url, 'laboratorio_nombre': laboratorio_nombre})


def listar_reportes(request):
    """Vista para listar todos los reportes registrados."""
    reportes = ReporteUsoLaboratorio.objects.all()
    return render(request, "listar_reportes.html", {"reportes": reportes})