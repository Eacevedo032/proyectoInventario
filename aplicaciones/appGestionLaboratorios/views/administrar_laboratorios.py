from decimal import Decimal
from django.forms import ValidationError
from django.utils import timezone
from itertools import groupby
from django.shortcuts import get_object_or_404, redirect, render
from aplicaciones.appGestionInventario.models import HistorialInventario, SolicitudLaboratorio, HorarioLaboratorio, UsoItemLaboratorio,Inventario
from django.contrib.auth.models import User
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades
from decimal import Decimal
from django.http import JsonResponse

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

#Vista para aprobar solicitudes
@csrf_exempt
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)

    # Verificar si la solicitud ya está aprobada
    if solicitud.estado == 'aprobada':
        return JsonResponse({'success': False, 'message': 'Esta solicitud ya fue aprobada.'})

    # Solo procesar solicitudes POST
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})

    # Validar descripción
    descripcion = json.loads(request.body).get('descripcion')
    if not descripcion:
        return JsonResponse({'success': False, 'message': 'La descripción es requerida.'})

    try:
        with transaction.atomic():
            # Verificar conflictos de horario
            if _tiene_conflictos_horario(solicitud):
                return JsonResponse({'success': False, 'message': 'El laboratorio ya está reservado en el horario solicitado.'})

            # Verificar disponibilidad de inventario
            items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)
            if not _verificar_inventario_suficiente(items_solicitados):
                return JsonResponse({'success': False, 'message': 'No hay suficiente inventario para uno o más productos solicitados.'})

            # Aprobar la solicitud y actualizar inventario
            _aprobar_solicitud_y_actualizar_inventario(solicitud, items_solicitados, descripcion, request.user)

            # Crear horario de reserva
            _crear_horario_reserva(solicitud)

            messages.success(request, 'La solicitud ha sido aprobada exitosamente.')
            return JsonResponse({'success': True, 'message': 'La solicitud ha sido aprobada exitosamente.'})

    except ValidationError as e:
        errors = ', '.join([error for field, error_list in e.message_dict.items() for error in error_list])
        return JsonResponse({'success': False, 'message': f'Errores de validación: {errors}'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error inesperado al aprobar la solicitud: {str(e)}'})

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

# Funciones auxiliares
def _tiene_conflictos_horario(solicitud):
    """Verifica si hay conflictos de horario para la solicitud."""
    return HorarioLaboratorio.objects.filter(
        laboratorio=solicitud.laboratorio,
        fecha_reserva=solicitud.fecha_reserva,
        hora_inicio__lt=solicitud.hora_fin,
        hora_fin__gt=solicitud.hora_inicio,
    ).exists()


def _verificar_inventario_suficiente(items_solicitados):
    """Verifica si hay suficiente inventario para todos los ítems solicitados."""
    productos_solicitados = {}
    for item in items_solicitados:
        inventario_item = item.inventario
        cantidad_solicitada = _convertir_cantidad(item.cantidad_utilizada, item.unidad_medida, inventario_item.unidad_medida)
        productos_solicitados[inventario_item.id_inventario] = productos_solicitados.get(inventario_item.id_inventario, 0) + cantidad_solicitada

    for producto_id, cantidad_total in productos_solicitados.items():
        inventario_item = Inventario.objects.get(id_inventario=producto_id)
        if inventario_item.cantidad_disponible < cantidad_total:
            return False
    return True


def _convertir_cantidad(cantidad, unidad_origen, unidad_destino):
    """Convierte la cantidad de una unidad a otra."""
    if unidad_origen != unidad_destino:
        try:
            return convertir_unidades(Decimal(str(cantidad)), unidad_origen=unidad_origen, unidad_destino=unidad_destino)
        except ValueError as e:
            raise ValidationError(f"Error al convertir unidades: {str(e)}")
    return Decimal(str(cantidad))


def _aprobar_solicitud_y_actualizar_inventario(solicitud, items_solicitados, descripcion, usuario):
    """Aprueba la solicitud y actualiza el inventario."""
    for item in items_solicitados:
        inventario_item = item.inventario
        cantidad_solicitada = _convertir_cantidad(item.cantidad_utilizada, item.unidad_medida, inventario_item.unidad_medida)
        inventario_item.cantidad_disponible -= cantidad_solicitada
        inventario_item.save()

        HistorialInventario.objects.create(
            inventario=inventario_item,
            cantidad_cambiada=cantidad_solicitada,
            unidad_medida=item.unidad_medida,
            cantidad_anterior=inventario_item.cantidad_disponible + cantidad_solicitada,
            fecha_cambio=timezone.now(),
            tipo_cambio='salida',
            modificado_por=usuario,
            descripcion=descripcion
        )

    solicitud.estado = 'aprobada'
    solicitud.save()


def _crear_horario_reserva(solicitud):
    """Crea un horario de reserva para la solicitud aprobada."""
    HorarioLaboratorio.objects.create(
        laboratorio=solicitud.laboratorio,
        fecha_reserva=solicitud.fecha_reserva,
        hora_inicio=solicitud.hora_inicio,
        hora_fin=solicitud.hora_fin,
    )