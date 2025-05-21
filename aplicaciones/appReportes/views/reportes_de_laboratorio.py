from datetime import datetime
from urllib.parse import urljoin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appReportes.models import ReporteUsoLaboratorio, ReporteFoto
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio
from django.contrib.auth.decorators import login_required

@login_required
def finalizar_uso(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)
    
    # Verificar que la solicitud esté aprobada
    if solicitud.estado != 'aprobada':
        messages.error(request, "Solo puedes finalizar solicitudes aprobadas")
        return redirect('reservar_laboratorio')

    if request.method == 'POST':
        # Procesar datos del formulario
        numero_estudiantes = request.POST.get('numero_estudiantes')
        estudiantes_masculinos = request.POST.get('estudiantes_masculinos')
        estudiantes_femeninos = request.POST.get('estudiantes_femeninos')
        horario_salida_real = request.POST.get('horario_salida_real')
        objetivo_practica = request.POST.get('objetivo_practica')
        fotos = request.FILES.getlist('fotos')

        # Validaciones básicas
        if not all([numero_estudiantes, objetivo_practica, horario_salida_real]):
            messages.error(request, "Campos obligatorios faltantes")
            return redirect('finalizar_uso', solicitud_id=solicitud.id)

        try:
            # Crear reporte
            reporte = ReporteUsoLaboratorio.objects.create(
                solicitud=solicitud,
                numero_estudiantes=numero_estudiantes,
                estudiantes_masculinos=estudiantes_masculinos,
                estudiantes_femeninos=estudiantes_femeninos,
                horario_salida_real=horario_salida_real,
                objetivo_practica=objetivo_practica
            )

            # Guardar fotos
            for foto in fotos:
                ReporteFoto.objects.create(reporte=reporte, imagen=foto)

            # Cambiar estado de la solicitud SOLO si todo está correcto
            solicitud.estado = 'completado'
            solicitud.save()

            messages.success(request, "Guardado exitosamente")
            return redirect('reservar_laboratorio')

        except Exception as e:
            messages.error(request, f"Error al crear formulario: {str(e)}")
            return redirect('finalizar_uso', solicitud_id=solicitud.id)

    # Si es GET, mostrar formulario con datos de la solicitud
    return render(request, 'finalizar_uso.html', {
        'solicitud': solicitud,
        'hoy': datetime.now().strftime("%Y-%m-%d"),
        'hora_fin': solicitud.hora_fin.strftime("%H:%M") if solicitud.hora_fin else ""
    })

def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteUsoLaboratorio, id=reporte_id)
    fotos = ReporteFoto.objects.filter(reporte=reporte)
    productos = UsoItemLaboratorio.objects.filter(solicitud=reporte.solicitud)
    
    # Obtener los datos de la solicitud relacionada
    solicitud = reporte.solicitud  # Asumiendo que tienes una relación ForeignKey o OneToOneField
    
    return render(request, 'detalle_reporte.html', {
        'reporte': reporte,
        'fotos': fotos,
        'laboratorio_nombre': solicitud.laboratorio if solicitud else "No especificado",
        'clase': solicitud.clase if solicitud else "No especificado",
        'asignatura': solicitud.asignatura if solicitud else "No especificado",
        'fecha_solicitud': solicitud.fecha_solicitud if solicitud else "No especificado",
        'fecha_reserva': solicitud.fecha_reserva if solicitud else "No especificado",
        'productos': productos,
    })


from django.core.paginator import Paginator
from django.db.models import Q

def listar_reportes(request):
    # Obtener todos los reportes
    reportes = ReporteUsoLaboratorio.objects.all().select_related('solicitud')
    
    # Obtener laboratorios únicos para el filtro
    laboratorios = SolicitudLaboratorio.objects.values_list('laboratorio', flat=True).distinct()
    
    # Aplicar filtros
    laboratorio = request.GET.get('laboratorio')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if laboratorio:
        reportes = reportes.filter(solicitud__laboratorio=laboratorio)
    
    if fecha_inicio and fecha_fin:
        reportes = reportes.filter(
            solicitud__fecha_reserva__range=[fecha_inicio, fecha_fin]
        )
    elif fecha_inicio:
        reportes = reportes.filter(
            solicitud__fecha_reserva__gte=fecha_inicio
        )
    elif fecha_fin:
        reportes = reportes.filter(
            solicitud__fecha_reserva__lte=fecha_fin
        )
    
    # Paginación (10 items por página)
    paginator = Paginator(reportes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'listar_reportes.html', {
        'page_obj': page_obj,
        'laboratorios': laboratorios,
    })