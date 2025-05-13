from urllib.parse import urljoin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appReportes.models import ReporteUsoLaboratorio, ReporteFoto
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio

def crear_reporte(request):
    """Vista para crear un nuevo reporte vinculado a una solicitud aprobada."""
    # Filtra las solicitudes que no tienen un reporte asociado
    solicitudes_aprobadas = SolicitudLaboratorio.objects.filter(
        estado='aprobada'
    ).exclude(reporteusolaboratorio__isnull=False)

    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        numero_estudiantes = request.POST.get('numero_estudiantes')
        estudiantes_masculinos = request.POST.get('estudiantes_masculinos')
        estudiantes_femeninos = request.POST.get('estudiantes_femeninos')
        clase = request.POST.get('clase')
        asignatura = request.POST.get('asignatura')
        horario_salida_real = request.POST.get('horario_salida_real')
        objetivo_practica = request.POST.get('objetivo_practica')
        fotos = request.FILES.getlist('fotos')  # Lista de archivos subidos

        # Validaciones de datos
        if not solicitud_id:
            messages.error(request, "Debes seleccionar una solicitud.")
            return redirect('crear_reporte')
        if not numero_estudiantes or not numero_estudiantes.isdigit():
            messages.error(request, "Debes ingresar un número válido de estudiantes.")
            return redirect('crear_reporte')
        if not objetivo_practica:
            messages.error(request, "Debes ingresar el objetivo de la práctica.")
            return redirect('crear_reporte')

        try:
            solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)

            # Crear el reporte
            reporte = ReporteUsoLaboratorio.objects.create(
                solicitud=solicitud,
                numero_estudiantes=int(numero_estudiantes),
                clase=clase,
                asignatura=asignatura,
                horario_salida_real=horario_salida_real,
                estudiantes_masculinos=int(estudiantes_masculinos),
                estudiantes_femeninos=int(estudiantes_femeninos),
                objetivo_practica=objetivo_practica,
            )

            # Guardar cada foto en `ReporteFoto`
            for foto in fotos:
                ReporteFoto.objects.create(reporte=reporte, imagen=foto)

            messages.success(request, "Reporte creado exitosamente.")
            return redirect('listar_reportes')

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return redirect('crear_reporte')

    return render(request, 'crear_reporte.html', {'solicitudes': solicitudes_aprobadas})

def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteUsoLaboratorio, id=reporte_id)
    fotos = ReporteFoto.objects.filter(reporte=reporte)  # Obtener imágenes asociadas

    return render(request, 'detalle_reporte.html', {
        'reporte': reporte,
        'fotos': fotos,
    })



def listar_reportes(request):
    """Vista para listar todos los reportes registrados."""
    reportes = ReporteUsoLaboratorio.objects.all()
    return render(request, "listar_reportes.html", {"reportes": reportes})