from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseServerError
import csv
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import ValidationError
from django.urls import reverse
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio
from django.db import transaction
from django.db.models import Q

@login_required
def reservar_laboratorio(request):
    modo = request.GET.get('modo', 'laboratorios') 
    mostrar_boton_recursos = True if modo == 'ambos' else False

    if request.method == 'POST':
        laboratorio = request.POST['laboratorio']
        fecha_reserva = request.POST['fecha_reserva']
        clase = request.POST.get('clase')
        asignatura = request.POST.get('asignatura')
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']
        objetivo_practica = request.POST.get('objetivo_practica')

        # Validación de hora
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")
        
        # Validaciones básicas
        if not all([laboratorio, fecha_reserva, clase, asignatura, hora_inicio, hora_fin, objetivo_practica]):
            messages.error(request, "Campos obligatorios faltantes")
            return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

        # Verificar solapamiento con otras solicitudes
        solapamiento = SolicitudLaboratorio.objects.filter(
            laboratorio=laboratorio,
            fecha_reserva=fecha_reserva,
        ).exclude(
            Q(hora_fin__lte=hora_inicio) | Q(hora_inicio__gte=hora_fin)
        ).exists()

        if solapamiento:
            messages.error(request, "Ya existe una reserva para el horario seleccionado.")
            return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

        # Crear solicitud
        solicitud = SolicitudLaboratorio(
            usuario=request.user,
            laboratorio=laboratorio,
            fecha_reserva=fecha_reserva,
            clase=clase,
            asignatura=asignatura,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            objetivo_practica=objetivo_practica,
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
            return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

        solicitud.save()
        messages.success(request, 'La solicitud de reserva se ha creado exitosamente.')
        return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

    # Filtros
    laboratorio = request.GET.get('laboratorio')
    fecha = request.GET.get('fecha')
    mostrar_historial = request.GET.get('mostrar_historial') == 'true'

    # Determinar si hay filtros activos (excluyendo parámetros de paginación y modo)
    tiene_filtros = any(key in request.GET for key in ['laboratorio', 'fecha', 'mostrar_historial'])

    # Fecha límite para mostrar solicitudes antiguas
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)

    # Query base - inicialmente solo pendientes si no hay filtros
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)
    
    # Si no hay filtros activos, mostrar solo pendientes
    if not tiene_filtros:
        solicitudes = solicitudes.filter(estado=SolicitudLaboratorio.PENDIENTE)

    # Filtros opcionales
    if laboratorio:
        solicitudes = solicitudes.filter(laboratorio=laboratorio)
    if fecha:
        solicitudes = solicitudes.filter(fecha_reserva=fecha)

    # Excluir solicitudes muy antiguas si no se activa historial completo
    if not mostrar_historial:
        solicitudes = solicitudes.exclude(fecha_reserva__lt=fecha_limite)

    # Clasificación por modo (laboratorios/ambos)
    if modo == 'ambos':
        solicitudes_filtradas = solicitudes.filter(tiene_recursos=True)
    elif modo == 'laboratorios':
        solicitudes_filtradas = solicitudes.filter(tiene_recursos=False)
    else:
        solicitudes_filtradas = solicitudes

    # Paginación
    solicitudes_combinadas = solicitudes_filtradas.order_by('-fecha_reserva', '-hora_inicio')
    paginator = Paginator(solicitudes_combinadas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Resumen de estado (siempre calculado sobre todas las solicitudes)
    solicitudes_todas = SolicitudLaboratorio.objects.filter(usuario=request.user)
    solicitudes_pendientes = solicitudes_todas.filter(estado='pendiente').count()
    solicitudes_aprobadas = solicitudes_todas.filter(estado='aprobada').count()
    solicitudes_rechazadas = solicitudes_todas.filter(estado='rechazada').count()

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
        'tiene_filtros': tiene_filtros,  # Para usar en la plantilla si es necesario
    })

@login_required
def enviar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)

    modo = request.GET.get('modo', 'laboratorios')

    if solicitud.estado != SolicitudLaboratorio.PENDIENTE:
        messages.error(request, "Solo se pueden enviar solicitudes en estado pendiente.")
        return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

    # Cambiar estado a "en revisión"
    solicitud.estado = SolicitudLaboratorio.EN_REVISION
    solicitud.save()
    
    messages.success(request, "La solicitud ha sido enviada y está en revisión.")
    return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")

#editar solicitud de laboratorio
@login_required
def editar_laboratorio(request, solicitud_id):
    # Obtener la solicitud de reserva a editar
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id, usuario=request.user)
    modo = request.GET.get('modo', 'laboratorios')

    # Verificar si el estado de la solicitud permite edición
    if solicitud.estado == SolicitudLaboratorio.PENDIENTE:
        # Si es un usuario con permisos, bloquear edición
        if request.user.is_superuser or request.user.has_perm('app.administrador') or request.user.has_perm('app.privilegiado'):
            messages.error(request, "Usuarios con privilegios no pueden editar reservas en estado pendiente.")
            return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")
    elif solicitud.estado == SolicitudLaboratorio.EN_REVISION:
            # Permitir edición solo a usuarios con privilegios
            if not (request.user.is_superuser or request.user.has_perm('app.administrador') or request.user.has_perm('app.privilegiado')):
                messages.error(request, "Solo los usuarios con privilegios pueden editar reservas en estado EN_REVISION.")
                return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")
    else:
                # Bloquear edición para cualquier otro estado
                messages.error(request, "No se pueden editar reservas en este estado.")
                return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")
            
    if request.method == 'POST':
        # Obtener los datos del formulario
        laboratorio = request.POST['laboratorio']
        asignatura = request.POST['asignatura']
        clase = request.POST['clase']
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']

        # Validación de hora
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect('editar_laboratorio', solicitud_id=solicitud.id)

        # Actualizar los datos de la reserva
        solicitud.laboratorio = laboratorio
        solicitud.asignatura = asignatura
        solicitud.clase = clase
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
        return redirect (f"{reverse('reservar_laboratorio')}?modo={modo}")

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
    modo = request.GET.get('modo', 'laboratorios') 
    
    # Verificar si la solicitud está en estado "pendiente" o "rechazada"
    if solicitud.estado not in ['pendiente', 'rechazada']:
        messages.error(request, "Solo se pueden eliminar solicitudes pendientes o rechazadas.")
        return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")
    
    # Eliminar la solicitud
    solicitud.delete()
    messages.success(request, "La solicitud ha sido eliminada correctamente.")
    
    return redirect(f"{reverse('reservar_laboratorio')}?modo={modo}")