# views.py
from itertools import groupby 
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.db import transaction
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo, convertir_unidades
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio
from inventario_nuevo.models import Producto

@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        usuario_id = request.POST.get('usuario')
        fecha_uso = request.POST.get('fecha_uso')

        producto_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad_utilizada[]')
        unidades_medida = request.POST.getlist('unidad_medida[]')

        # Validaciones básicas
        if not solicitud_id or not usuario_id or not fecha_uso:
            messages.error(request, "Faltan datos obligatorios.")
            return redirect('solicitar_recursos')

        # Verificar que al menos un producto fue seleccionado
        if not any(producto_ids):
            messages.error(request, "Debe seleccionar al menos un producto.")
            return redirect('solicitar_recursos')

        # Procesar cada producto
        items_validos = 0
        for i in range(len(producto_ids)):
            if not producto_ids[i]:  # Saltar productos vacíos
                continue

            try:
                producto = get_object_or_404(Producto, id=producto_ids[i])
                cantidad_utilizada_decimal = Decimal(cantidades[i])
                
                if cantidad_utilizada_decimal <= 0:
                    messages.error(request, "La cantidad a utilizar debe ser mayor a 0.")
                    return redirect('solicitar_recursos')

                unidad_medida = unidades_medida[i]
                unidad_producto = producto.unidad_medida.abreviatura if hasattr(producto.unidad_medida, 'abreviatura') else str(producto.unidad_medida)

                # Verificar compatibilidad de unidades
                unidades_equivalentes = {
                    'unidad': ['unidad', 'unidades'],
                    'kg': ['kg', 'kilogramo', 'kilogramos'],
                    'g': ['g', 'gramo', 'gramos'],
                    'l': ['l', 'litro', 'litros'],
                }

                unidades_compatibles = any(
                    str(unidad_medida).lower() in grupo and str(unidad_producto).lower() in grupo
                    for grupo in unidades_equivalentes.values()
                )

                if unidades_compatibles:
                    cantidad_convertida = cantidad_utilizada_decimal
                else:
                    try:
                        cantidad_convertida = convertir_unidades(
                            cantidad_utilizada_decimal, 
                            unidad_medida, 
                            unidad_producto
                        )
                    except ValueError:
                        messages.error(request, 
                            f"No se pueden convertir {unidad_medida} a {unidad_producto}. "
                            "Solicite items cuyas unidades de medida sean compatibles."
                        )
                        return redirect('solicitar_recursos')

                # Verificar disponibilidad
                if cantidad_convertida > producto.cantidad_disponible:
                    messages.error(request, 
                        f"La cantidad solicitada ({cantidad_convertida} {unidad_producto}) "
                        f"es mayor a la existente en Inventario ({producto.cantidad_disponible} {unidad_producto})."
                    )
                    return redirect('solicitar_recursos')

                # Crear registro de uso
                uso_item = UsoItemLaboratorio(
                    solicitud_id=solicitud_id,
                    producto=producto,
                    usuario_id=usuario_id,
                    cantidad_utilizada=cantidad_convertida,
                    unidad_medida=unidad_medida,
                    fecha_uso=fecha_uso,
                    cantidad_disponible_momento=producto.cantidad_disponible,
                    unidad_medida_momento=producto.unidad_medida,
                )
                uso_item.save()
                items_validos += 1

            except (InvalidOperation, IndexError, TypeError):
                messages.error(request, "La cantidad ingresada no es válida.")
                return redirect('solicitar_recursos')
            except Exception as e:
                messages.error(request, f"Error al procesar el producto: {str(e)}")
                return redirect('solicitar_recursos')

        if items_validos == 0:
            messages.error(request, "No se encontraron productos válidos para procesar.")
            return redirect('solicitar_recursos')

        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')
        return redirect('solicitar_recursos')
    
    # Código para GET requests
    solicitud_id = request.GET.get('solicitud_id')
    productos_disponibles = Producto.objects.filter(estado__estado='disponible').select_related('unidad_medida')

    # Obtener todas las solicitudes pendientes o aprobadas del usuario que pueden tener recursos
    solicitudes = SolicitudLaboratorio.objects.filter(
        usuario=request.user, 
        estado__in=['pendiente', 'aprobada'],
        tiene_recursos=True
    ).order_by('-fecha_reserva')
    
    # Si se proporcionó un solicitud_id, seleccionar esa solicitud por defecto
    solicitud_seleccionada = None
    if solicitud_id:
        try:
            solicitud_seleccionada = get_object_or_404(SolicitudLaboratorio, 
                                                     id=solicitud_id, 
                                                     usuario=request.user)
            # Verificar que la solicitud puede tener recursos
            if not solicitud_seleccionada.tiene_recursos:
                messages.warning(request, "Esta solicitud no está configurada para usar recursos.")
                return redirect('solicitar_recursos')
        except Http404:
            messages.error(request, "La solicitud especificada no existe o no pertenece a usted.")
            return redirect('solicitar_recursos')

    # Filtrar solicitudes de recursos
    fecha = request.GET.get('fecha')
    laboratorio = request.GET.get('laboratorio')
    solicitudes_recursos = UsoItemLaboratorio.objects.filter(usuario=request.user).select_related('producto', 'solicitud')

    if fecha:
        solicitudes_recursos = solicitudes_recursos.filter(fecha_uso=fecha)
    if laboratorio:
        solicitudes_recursos = solicitudes_recursos.filter(solicitud__laboratorio=laboratorio)

    # Filtro de historial
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)
    if request.GET.get('mostrar_historial') != 'true':
        solicitudes_recursos = solicitudes_recursos.exclude(fecha_uso__lt=fecha_limite)

    # Paginación
    solicitudes_recursos = solicitudes_recursos.order_by('-fecha_uso')
    paginator = Paginator(solicitudes_recursos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Estadísticas
    solicitudes_pendientes = UsoItemLaboratorio.objects.filter(
        usuario=request.user, 
        solicitud__estado='pendiente'
    ).count()
    
    solicitudes_aprobadas = UsoItemLaboratorio.objects.filter(
        usuario=request.user, 
        solicitud__estado='aprobada'
    ).count()
    
    solicitudes_rechazadas = UsoItemLaboratorio.objects.filter(
        usuario=request.user, 
        solicitud__estado='rechazada'
    ).count()

    laboratorios = SolicitudLaboratorio.objects.filter(
        usuario=request.user,
        tiene_recursos=True
    ).values('laboratorio').distinct()

    context = {
        'solicitudes': solicitudes,
        'solicitud_seleccionada': solicitud_seleccionada,
        'fecha_seleccionada': solicitud_seleccionada.fecha_reserva if solicitud_seleccionada else None,
        'productos_disponibles': productos_disponibles,
        'solicitudes_recursos': solicitudes_recursos,
        'page_obj': page_obj,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'laboratorios': laboratorios,
        'mostrar_historial': request.GET.get('mostrar_historial') == 'true',
    }

    return render(request, 'solicitar_recursos.html', context)


def obtener_items(request):   
    search_term = request.GET.get('search', '').strip()
    
    if not search_term:
        return JsonResponse({'status': 'error', 'message': 'Término de búsqueda requerido'}, status=400)
    
    items = Producto.objects.filter(
        estado__estado='disponible',
        nombre__icontains=search_term
    ).select_related('unidad_medida')[:10]  # Limitar a 10 resultados
    
    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'nombre': item.nombre,
            'cantidad_disponible': str(item.cantidad_disponible),
            'unidad_medida': item.unidad_medida.abreviatura,
            'texto_completo': f"{item.nombre} (Disponible: {item.cantidad_disponible} {item.unidad_medida.abreviatura})"
        })
    
    return JsonResponse({'status': 'success', 'items': items_data})

@login_required
def editar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    solicitud = uso_item.solicitud
    producto = uso_item.producto
    es_admin = request.user.is_staff or request.user.is_superuser

    if not es_admin and solicitud.estado != 'pendiente':
        messages.error(request, "Solo se pueden editar solicitudes pendientes.")
        return redirect('solicitar_recursos')

    if es_admin and solicitud.estado != 'en_revision':
        messages.error(request, "Solo se pueden editar solicitudes en revisión.")
        return redirect('revisar_solicitudes')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                cantidad_utilizada = request.POST.get('cantidad_utilizada', '').replace(',', '.')
                unidad_medida = request.POST.get('unidad_medida')
                comentario = request.POST.get('comentario', '')

                if not cantidad_utilizada or not unidad_medida:
                    raise ValueError("Todos los campos obligatorios deben completarse")
                
                try:
                    cantidad_decimal = Decimal(cantidad_utilizada)
                    if cantidad_decimal <= 0:
                        raise ValueError("La cantidad debe ser mayor a cero")
                except (InvalidOperation, TypeError):
                    raise ValueError("Cantidad ingresada no válida")

                unidad_producto_str = (
                    producto.unidad_medida.abreviatura 
                    if hasattr(producto.unidad_medida, 'abreviatura') 
                    else str(producto.unidad_medida)
                )

                if unidad_medida.lower() == unidad_producto_str.lower():
                    cantidad_convertida = cantidad_decimal
                else:
                    try:
                        cantidad_convertida = convertir_unidades(
                            cantidad_decimal,
                            unidad_medida,
                            unidad_producto_str
                        )
                    except ValueError:
                        raise ValueError(f"No se puede convertir {unidad_medida} a {unidad_producto_str}")

                if cantidad_convertida > producto.cantidad_disponible:
                    raise ValueError(
                        f"No hay suficiente stock. Disponible: {producto.cantidad_disponible} {unidad_producto_str}"
                    )

                uso_item.cantidad_utilizada = cantidad_decimal
                uso_item.unidad_medida = unidad_medida

                if es_admin and comentario:
                    uso_item.comentario_admin = comentario

                uso_item.save()
                messages.success(request, "Recurso actualizado correctamente")

                if es_admin:
                    return redirect('ver_items_solicitud', solicitud_id=solicitud.id)
                return redirect('ver_items_solicitud')

        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")
            return redirect('editar_recurso', uso_id=uso_id)

    unidad_actual = (
        uso_item.unidad_medida or
        (producto.unidad_medida.abreviatura if hasattr(producto.unidad_medida, 'abreviatura') else str(producto.unidad_medida))
    )

    return render(request, 'ver_items_solicitud.html', {
        'uso_item': uso_item,
        'unidad_actual': unidad_actual,
        'es_admin': es_admin,
        'producto': producto
    })

@login_required
def eliminar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    estado = uso_item.solicitud.estado.lower()

    if estado not in ['pendiente', 'en_revision', 'rechazada']:
        messages.error(request, "No se puede eliminar este recurso.")
        return redirect('solicitar_recursos')

    uso_item.delete()
    messages.success(request, "Recurso eliminado correctamente.")
    return redirect('solicitar_recursos')