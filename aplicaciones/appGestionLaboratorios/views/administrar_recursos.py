from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, timedelta
from aplicaciones.appGestionLaboratorios.models import SolicitudProductosInventario, HistorialInventario
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades
from inventario_nuevo.models import UnidadMedida

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required #Verifica si el usuario es administrador
@csrf_exempt
@login_required
def administracionRecursos(request):
    estado = request.GET.get('estado')
    producto = request.GET.get('producto')
    usuario = request.GET.get('usuario')

    # Base queryset: solicitudes distintas de "rechazada"
    solicitudes = SolicitudProductosInventario.objects.select_related(
        'usuario', 'producto'
    ).exclude(estado='rechazada')

    # Filtro por estado: si no hay filtro, solo "en_revision"
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    else:
        solicitudes = solicitudes.filter(estado='en_revision')

    # Filtro por nombre del producto (búsqueda parcial, insensible a mayúsculas)
    if producto:
        solicitudes = solicitudes.filter(producto__nombre__icontains=producto)

    # Filtro por nombre de usuario (búsqueda parcial, insensible a mayúsculas)
    if usuario:
        solicitudes = solicitudes.filter(usuario__username__icontains=usuario)

    # Ordenar por fecha de uso
    solicitudes = solicitudes.order_by('fecha_uso')

    # Agrupar solicitudes por usuario
    solicitudes_por_usuario = {}
    for solicitud in solicitudes:
        solicitudes_por_usuario.setdefault(solicitud.usuario, []).append(solicitud)

    # Paginación (10 elementos por página)
    paginator = Paginator(solicitudes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'administracionRecursos.html', {
        'solicitudes_por_usuario': solicitudes_por_usuario,
        'page_obj': page_obj
    })

@admin_required #Verifica si el usuario es administrador
@csrf_exempt
@login_required
@admin_required
@login_required
def aprobar_solicitud_producto(request, solicitud_id):
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('administracion_recursos')

    solicitud = get_object_or_404(SolicitudProductosInventario, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        messages.error(request, 'Esta solicitud ya fue aprobada.')
        return redirect('administracion_recursos')

    try:
        solicitud.full_clean()
    except ValidationError as e:
        messages.error(request, 'Errores de validación: ' + ', '.join(e.messages))
        return redirect('administracion_recursos')

    producto = solicitud.producto
    unidad_producto = producto.unidad_medida
    unidad_solicitada = UnidadMedida.objects.get(abreviatura=solicitud.unidad_medida)
    cantidad_anterior = Decimal(str(producto.cantidad_disponible))

    try:
        with transaction.atomic():
            # Convertir unidades si es necesario
            if unidad_producto != unidad_solicitada:
                cantidad_convertida = convertir_unidades(
                    Decimal(str(solicitud.cantidad_utilizada)),
                    unidad_origen=unidad_solicitada.abreviatura,
                    unidad_destino=unidad_producto.abreviatura,
                )
            else:
                cantidad_convertida = Decimal(str(solicitud.cantidad_utilizada))

            # Verificar disponibilidad
            if cantidad_anterior < cantidad_convertida:
                messages.error(request, f"No hay suficiente cantidad de {producto.nombre} en inventario.")
                return redirect('administracion_recursos')

            # Actualizar producto
            producto.cantidad_disponible = cantidad_anterior - cantidad_convertida
            producto.save()

            # Crear historial usando el motivo de la solicitud
            HistorialInventario.objects.create(
                producto=producto,
                cantidad_cambiada=cantidad_convertida,
                unidad_medida=solicitud.unidad_medida,
                cantidad_anterior=cantidad_anterior,
                fecha_cambio=timezone.now(),
                tipo_cambio='salida',
                modificado_por=request.user,
                descripcion=f"Solicitud #{solicitud.id}: {solicitud.motivo or 'Sin motivo especificado'}"
            )

            # Actualizar estado de la solicitud
            solicitud.estado = 'aprobada'
            solicitud.save()

            messages.success(request, 'Solicitud aprobada exitosamente.')
            return redirect('administracion_recursos')

    except Exception as e:
        messages.error(request, f'Error al aprobar solicitud: {str(e)}')
        return redirect('administracion_recursos')

from aplicaciones.appGestionLaboratorios.models import SolicitudProductosInventario

@admin_required #Verifica si el usuario es administrador
@csrf_exempt
@login_required
def rechazar_solicitud_producto(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProductosInventario, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede rechazar una solicitud aprobada.')
        return redirect('administracion_recursos')
    
    solicitud.estado = 'rechazada'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido rechazada exitosamente.')
    return redirect('administracion_recursos')

@admin_required #Verifica si el usuario es administrador
@login_required
def solicitud_pendiente_producto(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProductosInventario, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede marcar como pendiente una solicitud aprobada.')
        return redirect('administracion_recursos')

    solicitud.estado = 'pendiente'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido marcada como pendiente.')
    return redirect('administracion_recursos')