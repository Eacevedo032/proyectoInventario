from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.db import transaction
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo, convertir_unidades
from aplicaciones.appGestionLaboratorios.views import SolicitudLaboratorio, UsoItemLaboratorio
from inventario_nuevo.models import Producto, Subcategoria, Categoria

@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        usuario_id = request.POST.get('usuario')
        fecha_uso = request.POST.get('fecha_uso')

        producto_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad_utilizada[]')
        unidades_medida = request.POST.getlist('unidad_medida[]')

        if not solicitud_id or not usuario_id or not fecha_uso:
            messages.error(request, "Faltan datos obligatorios.")
            return redirect('solicitar_recursos')

        for i in range(len(producto_ids)):
            producto = get_object_or_404(Producto, id=producto_ids[i])
            try:
                cantidad_utilizada_decimal = Decimal(cantidades[i])
                if cantidad_utilizada_decimal <= 0:
                    messages.error(request, "La cantidad a utilizar debe ser mayor a 0.")
                    return redirect('solicitar_recursos')
            except (InvalidOperation, IndexError, TypeError):
                messages.error(request, "La cantidad ingresada no es válida.")
                return redirect('solicitar_recursos')

            unidad_medida = unidades_medida[i]
            unidad_producto = producto.unidad_medida.abreviatura if hasattr(producto.unidad_medida, 'abreviatura') else str(producto.unidad_medida)

            # Manejo especial para unidades equivalentes
            unidades_equivalentes = {
                'unidad': ['unidad', 'unidades', 'unidad'],
                'kg': ['kg', 'kilogramo', 'kilogramos'],
                'g': ['g', 'gramo', 'gramos'],
                'l': ['l', 'litro', 'litros'],
                # Puedes añadir más equivalencias aquí si es necesario
            }

            # Verificar si las unidades son equivalentes
            unidades_compatibles = False
            for grupo in unidades_equivalentes.values():
                if (str(unidad_medida).lower() in grupo and 
                    str(unidad_producto).lower() in grupo):
                    unidades_compatibles = True
                    break

            if unidades_compatibles:
                cantidad_convertida = cantidad_utilizada_decimal
            else:
                try:
                    cantidad_convertida = convertir_unidades(
                        cantidad_utilizada_decimal, 
                        unidad_medida, 
                        unidad_producto
                    )
                except ValueError as e:
                    messages.error(request, 
                        f"No se pueden convertir {unidad_medida} a {unidad_producto}. "
                        "Solicite items cuyas unidades de medida sean compatibles."
                    )
                    return redirect('solicitar_recursos')

            # Verificación de disponibilidad
            if cantidad_convertida > producto.cantidad_disponible:
                messages.error(request, 
                    f"La cantidad solicitada ({cantidad_convertida} {unidad_producto}) "
                    f"es mayor a la existente en Inventario ({producto.cantidad_disponible} {unidad_producto})."
                )
                return redirect('solicitar_recursos')

            # Registro del ítem
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

        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')

        return redirect('solicitar_recursos')

    # Parte GET de la vista
    categorias = Categoria.objects.all()
    
    # Filtrar solo solicitudes con tiene_recursos=True
    solicitudes = SolicitudLaboratorio.objects.filter(
        usuario=request.user, 
        estado='pendiente',
        tiene_recursos=True
    )

    # Filtros
    fecha = request.GET.get('fecha')
    laboratorio = request.GET.get('laboratorio')

    solicitudes_recursos = UsoItemLaboratorio.objects.filter(usuario=request.user)

    if fecha:
        solicitudes_recursos = solicitudes_recursos.filter(fecha_uso=fecha)
    if laboratorio:
        solicitudes_recursos = solicitudes_recursos.filter(solicitud__laboratorio=laboratorio)

    # Filtro de historial
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=30)

    if request.GET.get('mostrar_historial') != 'true':
        solicitudes_recursos = solicitudes_recursos.exclude(fecha_uso__lt=fecha_limite)

    # Ordenamiento y paginación
    solicitudes_recursos = solicitudes_recursos.order_by('-fecha_uso')
    paginator = Paginator(solicitudes_recursos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Resumen de solicitudes
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
        'solicitudes_recursos': solicitudes_recursos,
        'page_obj': page_obj,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'laboratorios': laboratorios,
        'categorias': categorias,
        'mostrar_historial': request.GET.get('mostrar_historial') == 'true',
    }

    return render(request, 'solicitar_recursos.html', context)

'''Después de groupby se construye un diccionario donde:
La clave (laboratorio) es el laboratorio asociado a la solicitud.
El valor es una lista de todas las solicitudes de recursos (items) que pertenecen a ese laboratorio.'''

# Vista para obtener las subcategorías de una categoría específica
from django.db.models import Q

@login_required
def obtener_subcategorias(request, categoria_id):
    try:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id
        ).order_by('nombre').values('id', 'nombre')
        return JsonResponse({'status': 'success', 'subcategorias': list(subcategorias)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

from django.http import JsonResponse

def obtener_items(request):
    categoria_id = request.GET.get('categoria_id')
    subcategoria_id = request.GET.get('subcategoria_id')
    
    if not categoria_id or not subcategoria_id:
        return JsonResponse({'status': 'error', 'message': 'Faltan parámetros'}, status=400)
    
    # Aquí deberías consultar tus items filtrando por categoría y subcategoría
    items = Producto.objects.filter(categoria_id=categoria_id, subcategoria_id=subcategoria_id, estado__estado='disponible')
    
    items_data = list(items.values('id', 'nombre', 'cantidad_disponible', 'unidad_medida__abreviatura', 'unidad_medida__nombre'))
    
    return JsonResponse({'status': 'success', 'items': items_data})

@login_required
def editar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    solicitud = uso_item.solicitud
    producto = uso_item.producto
    
    # Verificar permisos
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
                # Obtener datos del formulario
                cantidad_utilizada = request.POST.get('cantidad_utilizada', '').replace(',', '.')
                unidad_medida = request.POST.get('unidad_medida')
                comentario = request.POST.get('comentario', '')
                
                # Validaciones básicas
                if not cantidad_utilizada or not unidad_medida:
                    raise ValueError("Todos los campos obligatorios deben completarse")
                
                # Validación de cantidad
                try:
                    cantidad_decimal = Decimal(cantidad_utilizada)
                    if cantidad_decimal <= 0:
                        raise ValueError("La cantidad debe ser mayor a cero")
                except (InvalidOperation, TypeError):
                    raise ValueError("Cantidad ingresada no válida")
                
                # Obtener representación string de la unidad del producto
                if hasattr(producto.unidad_medida, 'abreviatura'):
                    unidad_producto_str = producto.unidad_medida.abreviatura
                else:
                    unidad_producto_str = str(producto.unidad_medida)
                
                # Verificar si las unidades son iguales (sin conversión necesaria)
                if unidad_medida.lower() == unidad_producto_str.lower():
                    cantidad_convertida = cantidad_decimal
                else:
                    try:
                        cantidad_convertida = convertir_unidades(
                            cantidad_decimal,
                            unidad_medida,
                            unidad_producto_str
                        )
                    except ValueError as e:
                        raise ValueError(f"No se puede convertir {unidad_medida} a {unidad_producto_str}")
                
                # Validar disponibilidad en inventario
                if cantidad_convertida > producto.cantidad_disponible:
                    raise ValueError(
                        f"No hay suficiente stock. Disponible: {producto.cantidad_disponible} {unidad_producto_str}"
                    )
                
                # Actualizar el ítem
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
    
    # Obtener la unidad de medida actual para el formulario
    if uso_item.unidad_medida:
        unidad_actual = uso_item.unidad_medida
    else:
        if hasattr(producto.unidad_medida, 'abreviatura'):
            unidad_actual = producto.unidad_medida.abreviatura
        else:
            unidad_actual = str(producto.unidad_medida)
    
    return render(request, 'ver_items_solicitud.html', {
        'uso_item': uso_item,
        'unidad_actual': unidad_actual,
        'es_admin': es_admin
    })

@login_required
def eliminar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    estado = uso_item.solicitud.estado.lower()

    # Solo eliminar si está en pendiente, en revisión o rechazada
    if estado not in ['pendiente', 'en_revision', 'rechazada']:
        messages.error(request, "Solo se pueden eliminar ítems de solicitudes pendientes, en revisión o rechazadas.")
        return redirect('solicitar_recursos')

    uso_item.delete()
    messages.success(request, "Ítem eliminado correctamente.")
    return redirect('solicitar_recursos')
