from decimal import Decimal
from django.forms import ValidationError
from django.utils import timezone
from itertools import groupby
from django.shortcuts import get_object_or_404, redirect, render
from aplicaciones.appGestionInventario.models import HistorialInventario, SolicitudLaboratorio, HorarioLaboratorio, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.db import transaction

#views solo para opciones de administrador
# Vista para administrar las solicitudes de laboratorio con ítems solicitados
def administracionLaboratorios(request):
    # Obtener todas las solicitudes junto con los ítems solicitados
    solicitudes = SolicitudLaboratorio.objects.select_related('usuario').order_by('usuario__username')
    
    # Diccionario para almacenar solicitudes agrupadas por usuario con sus ítems
    solicitudes_por_usuario = {}
    for usuario, solicitudes_usuario in groupby(solicitudes, lambda s: s.usuario):
        solicitudes_usuario_list = list(solicitudes_usuario)
        
        # Agregar los ítems solicitados para cada solicitud
        for solicitud in solicitudes_usuario_list:
            solicitud.items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)
        
        solicitudes_por_usuario[usuario] = solicitudes_usuario_list

    return render(request, 'administracionLaboratorios.html', {
        'solicitudes_por_usuario': solicitudes_por_usuario
    })

#para ver los recursos a utilizar en el laboratorio
def ver_items_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

    return render(request, 'ver_items_solicitud.html', {
        'solicitud': solicitud,
        'items_solicitados': items_solicitados
    })

# Vista para aprobar solicitudes y actualizar inventario
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    if solicitud.estado == 'aprobada':
        messages.error(request, 'Esta solicitud ya fue aprobada.')
        return redirect('administracion_laboratorios')

    try:
        solicitud.full_clean()
    except ValidationError as e:
        for field, error_list in e.message_dict.items():
            for error in error_list:
                messages.error(request, error)
                solicitud.estado = 'rechazada'
        solicitud.save()
        return redirect('administracion_laboratorios')

    # Verificamos si el laboratorio está disponible
    conflictos = HorarioLaboratorio.objects.filter(
        laboratorio=solicitud.laboratorio,
        fecha_reserva=solicitud.fecha_reserva,
        hora_inicio__lt=solicitud.hora_fin,
        hora_fin__gt=solicitud.hora_inicio,
    )

    if conflictos.exists():
        messages.error(request, 'El laboratorio ya está reservado en el horario solicitado.')
        return redirect('administracion_laboratorios')

    # Si no hay conflictos, procedemos a aprobar la solicitud.
    solicitud.estado = 'aprobada'

    with transaction.atomic():
        items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

        for item in items_solicitados:
            inventario_item = item.inventario  # Cambiado a 'inventario'

            if Decimal(inventario_item.cantidad_disponible) >= Decimal(item.cantidad_utilizada):
                inventario_item.cantidad_disponible = Decimal(inventario_item.cantidad_disponible) - Decimal(item.cantidad_utilizada) 
                inventario_item.save()

                HistorialInventario.objects.create(
                    inventario=inventario_item,
                    cantidad_cambiada=item.cantidad_utilizada,
                    fecha_cambio=timezone.now(),
                    tipo_cambio='salida'
                )
            else:
                messages.error(request, f"No hay suficiente cantidad de {inventario_item.nombre} en inventario.")
                return redirect('administracion_laboratorios')

        # Registrar horario de ocupación
        HorarioLaboratorio.objects.create(
            laboratorio=solicitud.laboratorio,
            fecha_reserva=solicitud.fecha_reserva,
            hora_inicio=solicitud.hora_inicio,
            hora_fin=solicitud.hora_fin,
        )

        solicitud.save()
        messages.success(request, 'La solicitud ha sido aprobada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para rechazar solicitudes
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede rechazar una solicitud aprobada.')
        return redirect('administracion_laboratorios')
    
    solicitud.estado = 'rechazada'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido rechazada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para solicitudes pendientes
def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede marcar como pendiente una solicitud aprobada.')
        return redirect('administracion_laboratorios')
    
    solicitud.estado = 'pendiente'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido marcada como pendiente.')
    return redirect('administracion_laboratorios')