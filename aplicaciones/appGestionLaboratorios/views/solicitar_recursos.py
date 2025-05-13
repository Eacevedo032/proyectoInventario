from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo, convertir_unidades
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
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user, estado='pendiente')

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
        usuario=request.user
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
    
    if uso_item.solicitud.estado != 'pendiente':
        messages.error(request, "Solo se pueden editar solicitudes pendientes.")
        return redirect('solicitar_recursos')
    
    if request.method == 'POST':
        cantidad_utilizada = request.POST.get('cantidad_utilizada').replace(',', '.')
        unidad_medida = request.POST.get('unidad_medida')
        
        try:
            cantidad_utilizada_decimal = Decimal(cantidad_utilizada)
            if cantidad_utilizada_decimal <= 0:
                messages.error(request, "La cantidad debe ser mayor a 0.")
                return redirect('editar_recurso', uso_id=uso_item.id)
        except (InvalidOperation, TypeError):
            messages.error(request, "Cantidad ingresada no válida.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        try:
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, uso_item.producto.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {uso_item.producto.unidad_medida}.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        if cantidad_convertida > uso_item.producto.cantidad_disponible:
            messages.error(request, "Cantidad solicitada mayor a la existente en inventario.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        uso_item.cantidad_utilizada = cantidad_utilizada_decimal
        uso_item.unidad_medida = unidad_medida
        uso_item.save()
        messages.success(request, "Solicitud actualizada correctamente.")
        return redirect('solicitar_recursos')
    
    return render(request, 'editar_recurso.html', {'uso_item': uso_item})

@login_required
def eliminar_recurso(request, uso_id):
    # Obtener la solicitud de recurso
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    
    # Verificar si la solicitud está en estado "pendiente" o "rechazada"
    if uso_item.solicitud.estado not in ['pendiente', 'rechazada']:
        messages.error(request, "Solo se pueden eliminar solicitudes pendientes o rechazadas.")
        return redirect('solicitar_recursos')
    
    # Eliminar la solicitud
    uso_item.delete()
    messages.success(request, "La solicitud ha sido eliminada correctamente.")
    
    return redirect('solicitar_recursos')