from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseServerError
import csv
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import ValidationError
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio
from django.db import transaction


@login_required
def reservar_laboratorio(request):
    modo = request.GET.get('modo', 'laboratorios') 
    mostrar_boton_recursos = True if modo == 'ambos' else False

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
            # Definir el valor del campo basado en el parámetro "modo"
            if modo == 'laboratorios':
                solicitud.tiene_recursos = False
            elif modo == 'ambos':
                solicitud.tiene_recursos = True
            solicitud.full_clean()
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
                for error in error_list:
                    messages.error(request, error)
            return redirect('reservar_laboratorio')

        solicitud.save()
        messages.success(request, 'La solicitud de reserva se ha creado exitosamente.')
        return redirect('reservar_laboratorio')

    # Filtros
    laboratorio = request.GET.get('laboratorio')
    fecha = request.GET.get('fecha')
    mostrar_historial = request.GET.get('mostrar_historial') == 'true'

    # Fecha límite para mostrar solicitudes antiguas
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)

    # Query base
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    # Filtros opcionales
    if laboratorio:
        solicitudes = solicitudes.filter(laboratorio=laboratorio)
    if fecha:
        solicitudes = solicitudes.filter(fecha_reserva=fecha)

    # Excluir solicitudes muy antiguas si no se activa historial completo
    if not mostrar_historial:
        solicitudes = solicitudes.exclude(fecha_reserva__lt=fecha_limite)

    # Clasificación
    if modo == 'ambos':
        solicitudes_filtradas = solicitudes.filter(tiene_recursos=True)
    elif modo == 'laboratorios':
        solicitudes_filtradas = solicitudes.filter(tiene_recursos=False)
    else:
        solicitudes_filtradas = solicitudes


    # Paginación unificada (puedes paginar por separado si prefieres)
    solicitudes_combinadas = solicitudes_filtradas.order_by('-fecha_reserva', '-hora_inicio')
    paginator = Paginator(solicitudes_combinadas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Resumen de estado
    solicitudes_pendientes = solicitudes.filter(estado='pendiente').count()
    solicitudes_aprobadas = solicitudes.filter(estado='aprobada').count()
    solicitudes_rechazadas = solicitudes.filter(estado='rechazada').count()

    # Lista de laboratorios disponibles para el filtro
    laboratorios = SolicitudLaboratorio.objects.filter(usuario=request.user).values('laboratorio').distinct()

    return render(request, 'reservar_laboratorio.html', {
        'page_obj': page_obj,
        'solicitudes_filtradas': solicitudes_combinadas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'laboratorios': laboratorios,
        'mostrar_historial': mostrar_historial,
        'mostrar_boton_recursos': mostrar_boton_recursos,
    })

@login_required
def enviar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)

    if solicitud.estado != SolicitudLaboratorio.PENDIENTE:
        messages.error(request, "Solo se pueden enviar solicitudes en estado pendiente.")
        return redirect('reservar_laboratorio')

    # Cambiar estado a "en revisión"
    solicitud.estado = SolicitudLaboratorio.EN_REVISION
    solicitud.save()
    
    messages.success(request, "La solicitud ha sido enviada y está en revisión.")
    return redirect('reservar_laboratorio')

#editar solicitud de laboratorio
@login_required
def editar_laboratorio(request, solicitud_id):
    # Obtener la solicitud de reserva a editar
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)

    # Verificar si el estado de la solicitud permite edición
    if solicitud.estado == SolicitudLaboratorio.PENDIENTE:
        # Si es un usuario con permisos, bloquear edición
        if request.user.is_superuser or request.user.has_perm('app.administrador') or request.user.has_perm('app.privilegiado'):
            messages.error(request, "Usuarios con privilegios no pueden editar reservas en estado pendiente.")
            return redirect('reservar_laboratorio')
    elif solicitud.estado == SolicitudLaboratorio.EN_REVISION:
            # Permitir edición solo a usuarios con privilegios
            if not (request.user.is_superuser or request.user.has_perm('app.administrador') or request.user.has_perm('app.privilegiado')):
                messages.error(request, "Solo los usuarios con privilegios pueden editar reservas en estado EN_REVISION.")
                return redirect('reservar_laboratorio')
    else:
                # Bloquear edición para cualquier otro estado
                messages.error(request, "No se pueden editar reservas en este estado.")
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

@login_required
def eliminar_solicitud(request, solicitud_id):
    # Obtener la solicitud de producto
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    # Verificar si la solicitud está en estado "pendiente" o "rechazada"
    if solicitud.estado not in ['pendiente', 'rechazada']:
        messages.error(request, "Solo se pueden eliminar solicitudes pendientes o rechazadas.")
        return redirect('reservar_laboratorio')
    
    # Eliminar la solicitud
    solicitud.delete()
    messages.success(request, "La solicitud ha sido eliminada correctamente.")
    
    return redirect('reservar_laboratorio')