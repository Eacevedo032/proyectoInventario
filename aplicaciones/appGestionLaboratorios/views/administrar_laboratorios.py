from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from itertools import groupby
from django.contrib.auth.decorators import login_required
import json
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio, HorarioLaboratorio, HistorialInventario
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades
from inventario_nuevo.models import UnidadMedida
from django.utils.timezone import now

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required #Verifica si el usuario es administrador
@login_required
def administracionLaboratorios(request):
    estado = request.GET.get('estado')
    laboratorio = request.GET.get('laboratorio')
    usuario = request.GET.get('usuario')

    # Por defecto solo solicitudes en revisión
    if estado:
        solicitudes = SolicitudLaboratorio.objects.select_related('usuario').exclude(estado='rechazada').filter(estado=estado)
    else:
        solicitudes = SolicitudLaboratorio.objects.select_related('usuario').exclude(estado='rechazada').filter(estado='en_revision')

    # Filtros adicionales
    if laboratorio:
        solicitudes = solicitudes.filter(laboratorio__icontains=laboratorio)
    if usuario:
        solicitudes = solicitudes.filter(usuario__username__icontains=usuario)

    # Ocultar solicitudes aprobadas antiguas (más de 30 días) si no se solicita historial
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)

    if request.GET.get('mostrar_historial') != 'true':
        solicitudes = solicitudes.exclude(estado='aprobada', fecha_reserva__lt=fecha_limite)

    # Ordenar por usuario
    solicitudes = solicitudes.order_by('usuario__username')

    # Paginación
    paginator = Paginator(solicitudes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Agrupar solicitudes por usuario
    solicitudes_por_usuario = {}
    for usuario, solicitudes_usuario in groupby(page_obj, lambda s: s.usuario):
        solicitudes_usuario_list = list(solicitudes_usuario)
        for solicitud in solicitudes_usuario_list:
            solicitud.items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)
        solicitudes_por_usuario[usuario] = solicitudes_usuario_list

    return render(request, 'administracionLaboratorios.html', {
        'solicitudes_por_usuario': solicitudes_por_usuario,
        'page_obj': page_obj
    })

@admin_required
@login_required
def aprobar_solicitud(request, solicitud_id):
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('administracion_laboratorios')

    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        messages.error(request, 'Esta solicitud ya fue aprobada.')
        return redirect('administracion_laboratorios')

    # Validaciones internas del modelo
    try:
        solicitud.full_clean()
    except ValidationError as e:
        messages.error(request, 'Errores de validación: ' + ', '.join(e.messages))
        return redirect('administracion_laboratorios')

    # Verificar conflictos de horario
    conflictos = HorarioLaboratorio.objects.filter(
        laboratorio=solicitud.laboratorio,
        fecha_reserva=solicitud.fecha_reserva,
        hora_inicio__lt=solicitud.hora_fin,
        hora_fin__gt=solicitud.hora_inicio,
    )
    if conflictos.exists():
        messages.error(request, 'El laboratorio ya está reservado en el horario solicitado.')
        return redirect('administracion_laboratorios')

    try:
        with transaction.atomic():
            solicitud.estado = SolicitudLaboratorio.APROBADA
            solicitud.save()

            # Registrar horario
            HorarioLaboratorio.objects.create(
                laboratorio=solicitud.laboratorio,
                fecha_reserva=solicitud.fecha_reserva,
                hora_inicio=solicitud.hora_inicio,
                hora_fin=solicitud.hora_fin,
            )

            # Obtener ítems relacionados
            items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

            for item in items_solicitados:
                producto = item.producto
                cantidad_anterior = Decimal(str(producto.cantidad_disponible))
                unidad_producto = producto.unidad_medida
                unidad_solicitada = UnidadMedida.objects.get(abreviatura=item.unidad_medida)

                # Convertir unidades si es necesario
                if unidad_producto != unidad_solicitada:
                    try:
                        cantidad_solicitada_convertida = convertir_unidades(
                            Decimal(str(item.cantidad_utilizada)),
                            unidad_origen=unidad_solicitada.abreviatura,
                            unidad_destino=unidad_producto.abreviatura
                        )
                    except ValueError as e:
                        messages.error(request, f"Error al convertir unidades: {e}")
                        raise  # Lanza para hacer rollback del atomic
                else:
                    cantidad_solicitada_convertida = Decimal(str(item.cantidad_utilizada))

                if cantidad_anterior < cantidad_solicitada_convertida:
                    messages.error(request, f"No hay suficiente cantidad de {producto.nombre}.")
                    raise ValueError("Cantidad insuficiente")

                # Actualizar inventario
                producto.cantidad_disponible = cantidad_anterior - cantidad_solicitada_convertida
                producto.save()

                # Registrar historial
                historial = HistorialInventario.objects.create(
                    producto=producto,
                    cantidad_anterior=cantidad_anterior,
                    cantidad_cambiada=cantidad_solicitada_convertida,
                    unidad_medida=unidad_producto.abreviatura,
                    fecha_cambio=timezone.now().date(),
                    tipo_cambio='salida',
                    modificado_por=request.user,
                    descripcion=solicitud.objetivo_practica
                )

            messages.success(request, 'La solicitud ha sido aprobada exitosamente.')

    except Exception as e:
        messages.error(request, f"Ocurrió un error al procesar la solicitud: {e}")

    return redirect('administracion_laboratorios')

# Vista para rechazar solicitudes
@admin_required #Verifica si el usuario es administrador
@csrf_exempt
@login_required
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
@admin_required #Verifica si el usuario es administrador
def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede marcar como pendiente una solicitud aprobada.')
        return redirect('administracion_laboratorios')
    
    solicitud.estado = 'pendiente'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido marcada como pendiente.')
    return redirect('administracion_laboratorios')

#para ver los recursos a utilizar en el laboratorio
@login_required
def ver_items_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

    return render(request, 'ver_items_solicitud.html', {
        'solicitud': solicitud,
        'items_solicitados': items_solicitados
    })