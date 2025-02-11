from decimal import Decimal
from django.forms import ValidationError
from django.utils import timezone
from itertools import groupby
from django.shortcuts import get_object_or_404, redirect, render
from aplicaciones.appGestionInventario.models import HistorialInventario, SolicitudLaboratorio, HorarioLaboratorio, UsoItemLaboratorio
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

# Vista para aprobar solicitudes
@csrf_exempt
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        return JsonResponse({
            'success': False,
            'message': 'Esta solicitud ya fue aprobada.'
        })

    if request.method == 'POST':
        data = json.loads(request.body)
        descripcion = data.get('descripcion')

        if not descripcion:
            return JsonResponse({
                'success': False,
                'message': 'La descripción es requerida.'
            })

        try:
            solicitud.full_clean()
        except ValidationError as e:
            errors = []
            for field, error_list in e.message_dict.items():
                for error in error_list:
                    errors.append(error)
            return JsonResponse({
                'success': False,
                'message': 'Errores de validación: ' + ', '.join(errors)
            })

        conflictos = HorarioLaboratorio.objects.filter(
            laboratorio=solicitud.laboratorio,
            fecha_reserva=solicitud.fecha_reserva,
            hora_inicio__lt=solicitud.hora_fin,
            hora_fin__gt=solicitud.hora_inicio,
        )

        if conflictos.exists():
            return JsonResponse({
                'success': False,
                'message': 'El laboratorio ya está reservado en el horario solicitado.'
            })

        solicitud.estado = 'aprobada'

        try:
            with transaction.atomic():
                items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

                for item in items_solicitados:
                    inventario_item = item.inventario
                    unidad_inventario = inventario_item.unidad_medida
                    unidad_solicitada = item.unidad_medida
                    cantidad_anterior = Decimal(str(inventario_item.cantidad_disponible))

                    if unidad_inventario != unidad_solicitada:
                        try:
                            cantidad_solicitada_convertida = convertir_unidades(
                                Decimal(str(item.cantidad_utilizada)),
                                unidad_origen=unidad_solicitada,
                                unidad_destino=unidad_inventario,
                            )
                        except ValueError as e:
                            return JsonResponse({
                                'success': False,
                                'message': f"Error al convertir unidades: {str(e)}"
                            })
                    else:
                        cantidad_solicitada_convertida = Decimal(str(item.cantidad_utilizada))

                    if cantidad_anterior >= cantidad_solicitada_convertida:
                        inventario_item.cantidad_disponible = cantidad_anterior - cantidad_solicitada_convertida
                        inventario_item.save()

                        HistorialInventario.objects.create(
                            inventario=inventario_item,
                            cantidad_cambiada=cantidad_solicitada_convertida,
                            unidad_medida=item.unidad_medida,
                            cantidad_anterior=cantidad_anterior,
                            fecha_cambio=timezone.now(),
                            tipo_cambio='salida',
                            modificado_por=request.user,
                            descripcion=descripcion
                        )
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': f"No hay suficiente cantidad de {inventario_item.nombre} en inventario."
                        })

                HorarioLaboratorio.objects.create(
                    laboratorio=solicitud.laboratorio,
                    fecha_reserva=solicitud.fecha_reserva,
                    hora_inicio=solicitud.hora_inicio,
                    hora_fin=solicitud.hora_fin,
                )

                solicitud.save()
                messages.success(request, 'La solicitud ha sido aprobada exitosamente.')

                return JsonResponse({
                    'success': True,
                    'message': 'La solicitud ha sido aprobada exitosamente.'
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Error inesperado al aprobar la solicitud: {str(e)}"
            })

    return JsonResponse({
        'success': False,
        'message': 'Método no permitido.'
    })

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