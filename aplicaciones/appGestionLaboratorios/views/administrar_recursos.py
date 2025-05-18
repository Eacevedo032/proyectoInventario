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

    solicitudes = SolicitudProductosInventario.objects.select_related(
        'usuario', 'producto'
    ).order_by('-fecha_uso')

    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    if producto:
        solicitudes = solicitudes.filter(producto__nombre__icontains=producto)
    if usuario:
        solicitudes = solicitudes.filter(usuario__username__icontains=usuario)

    # Agrupar por usuario
    solicitudes_por_usuario = {}
    for solicitud in solicitudes:
        if solicitud.usuario not in solicitudes_por_usuario:
            solicitudes_por_usuario[solicitud.usuario] = []
        solicitudes_por_usuario[solicitud.usuario].append(solicitud)

    # Paginación
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
def aprobar_solicitud_producto(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudProductosInventario, id=solicitud_id)

    if solicitud.estado == 'aprobada':
        return JsonResponse({'success': False, 'message': 'Esta solicitud ya fue aprobada.'})

    if request.method == 'POST':
        data = json.loads(request.body)
        descripcion = data.get('descripcion')

        if not descripcion:
            return JsonResponse({'success': False, 'message': 'La descripción es requerida.'})

        try:
            solicitud.full_clean()
        except ValidationError as e:
            errores = []
            for field, error_list in e.message_dict.items():
                for error in error_list:
                    errores.append(error)
            return JsonResponse({
                'success': False,
                'message': 'Errores de validación: ' + ', '.join(errores)
            })

        producto = solicitud.producto
        unidad_producto = producto.unidad_medida
        unidad_solicitada = UnidadMedida.objects.get(abreviatura=solicitud.unidad_medida)
        cantidad_anterior = Decimal(str(producto.cantidad_disponible))

        if unidad_producto != unidad_solicitada:
            try:
                cantidad_convertida = convertir_unidades(
                    Decimal(str(solicitud.cantidad_utilizada)),
                    unidad_origen=unidad_solicitada.abreviatura,
                    unidad_destino=unidad_producto.abreviatura,
                )
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'message': f"Error al convertir unidades: {str(e)}"
                })
        else:
            cantidad_convertida = Decimal(str(solicitud.cantidad_utilizada))

        if cantidad_anterior >= cantidad_convertida:
            try:
                with transaction.atomic():
                    producto.cantidad_disponible = cantidad_anterior - cantidad_convertida
                    producto.save()

                    HistorialInventario.objects.create(
                        producto=producto,
                        cantidad_cambiada=cantidad_convertida,
                        unidad_medida=unidad_solicitada,
                        cantidad_anterior=cantidad_anterior,
                        fecha_cambio=timezone.now(),
                        tipo_cambio='salida',
                        modificado_por=request.user,
                        descripcion=descripcion
                    )

                    solicitud.estado = 'aprobada'
                    solicitud.save()

                    messages.success(request, 'La solicitud ha sido aprobada exitosamente.')

                    return JsonResponse({'success': True, 'message': 'La solicitud ha sido aprobada exitosamente.'})

            except Exception as e:
                return JsonResponse({'success': False, 'message': f"Error al aprobar solicitud: {str(e)}"})
        else:
            return JsonResponse({'success': False, 'message': f"No hay suficiente cantidad de {producto.nombre} en inventario."})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

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