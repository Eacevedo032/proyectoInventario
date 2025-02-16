from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import ValidationError
from aplicaciones.appGestionInventario.models import SolicitudLaboratorio

@login_required
def reservar_laboratorio(request):
    if request.method == 'POST':
        laboratorio = request.POST['laboratorio']
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']

        # Validación de hora
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect('reservar_laboratorio')

        # Crear solicitud
        solicitud = SolicitudLaboratorio(
            usuario=request.user,
            laboratorio=laboratorio,
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=SolicitudLaboratorio.PENDIENTE,
        )

        try:
            # Validar que la solicitud no se superponga con otra solicitud
            solicitud.full_clean()
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
                for error in error_list:
                    messages.error(request, error)
            return redirect('reservar_laboratorio')

        solicitud.save()
        messages.success(request, 'La solicitud de reserva se ha creado exitosamente.')
        return redirect('reservar_laboratorio')

    # Filtros avanzados
    laboratorio = request.GET.get('laboratorio')
    fecha = request.GET.get('fecha')

    # Obtener todas las solicitudes del usuario autenticado, ordenadas de la más reciente a la más antigua
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    # Aplicar filtros
    if laboratorio:
        solicitudes = solicitudes.filter(laboratorio=laboratorio)
    if fecha:
        solicitudes = solicitudes.filter(fecha_reserva=fecha)

    # Ocultar solicitudes aprobadas antiguas (más de 30 días)
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)  # Mostrar solo las aprobadas en los últimos 30 días

    # Si el usuario no ha activado "mostrar historial completo", ocultar las aprobadas antiguas
    if request.GET.get('mostrar_historial') != 'true':
        solicitudes = solicitudes.exclude(fecha_reserva__lt=fecha_limite)

    # Ordenar por fecha y hora de inicio
    solicitudes = solicitudes.order_by('-fecha_reserva', '-hora_inicio')

    # Paginación
    paginator = Paginator(solicitudes, 10)  # 10 solicitudes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Resumen de solicitudes
    solicitudes_pendientes = solicitudes.filter(estado='pendiente').count()
    solicitudes_aprobadas = solicitudes.filter(estado='aprobada').count()
    solicitudes_rechazadas = solicitudes.filter(estado='rechazada').count()

    # Laboratorios para el filtro
    laboratorios = SolicitudLaboratorio.objects.filter(usuario=request.user).values('laboratorio').distinct()

    return render(request, 'reservar_laboratorio.html', {
        'page_obj': page_obj,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'laboratorios': laboratorios,
        'mostrar_historial': request.GET.get('mostrar_historial') == 'true',
    })

#editar solicitud de laboratorio
@login_required
def editar_laboratorio(request, solicitud_id):
    # Obtener la solicitud de reserva a editar
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)

    # Solo permitir editar si la reserva está en estado "pendiente"
    if solicitud.estado != SolicitudLaboratorio.PENDIENTE:
        messages.error(request, "Solo se pueden editar reservas en estado pendiente.")
        return redirect('reservar_laboratorio')

    if request.method == 'POST':
        # Obtener los datos del formulario
        laboratorio = request.POST['laboratorio']
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']

        # Validación de hora
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect('editar_laboratorio', solicitud_id=solicitud.id)

        # Actualizar los datos de la reserva
        solicitud.laboratorio = laboratorio
        solicitud.fecha_reserva = fecha_reserva
        solicitud.hora_inicio = hora_inicio
        solicitud.hora_fin = hora_fin

        try:
            # Validar que la reserva no se superponga con otra
            solicitud.full_clean()
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
                for error in error_list:
                    messages.error(request, error)
            return redirect('editar_laboratorio', solicitud_id=solicitud.id)

        solicitud.save()
        messages.success(request, 'La reserva se ha actualizado exitosamente.')
        return redirect('reservar_laboratorio')

    # Obtener laboratorios para el formulario
    laboratorio = SolicitudLaboratorio.objects.filter(usuario=request.user).values('laboratorio').distinct()

    return render(request, 'editar_laboratorio.html', {
        'solicitud': solicitud,
        'laboratorio': laboratorio,
    })

#eliminar solicitud de laboratorio
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'La solicitud ha sido eliminada exitosamente.')
        return redirect('reservar_laboratorio')  
    return render(request, 'reservar_laboratorio.html', {'solicitud': solicitud})