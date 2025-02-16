from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import Categoria, Inventario, SolicitudLaboratorio, SubCategoria, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades

# Vista para solicitar recursos desde una cuenta de usuario sin privilegios de administrador
@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
        # Procesar la solicitud de recursos
        solicitud_id = request.POST.get('solicitud')
        inventario_id = request.POST.get('inventario')
        usuario_id = request.POST.get('usuario')
        cantidad_utilizada = request.POST.get('cantidad_utilizada')
        unidad_medida = request.POST.get('unidad_medida')
        fecha_uso = request.POST.get('fecha_uso')

        # Obtener el inventario correspondiente
        inventario = get_object_or_404(Inventario, id_inventario=inventario_id)

        # Validación de cantidad ingresada que sea mayor a 0
        try:
            cantidad_utilizada_decimal = Decimal(cantidad_utilizada)
            if cantidad_utilizada_decimal <= 0:
                messages.error(request, "La cantidad a utilizar debe ser mayor a 0.")
                return redirect('solicitar_recursos')
        except (InvalidOperation, TypeError):
            messages.error(request, "La cantidad ingresada no es válida.")
            return redirect('solicitar_recursos')

        # Hacemos la conversión de la cantidad a la unidad del inventario
        try:
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, inventario.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {inventario.unidad_medida}.")
            return redirect('solicitar_recursos')

        # Verificamos si la cantidad solicitada es mayor que la disponible
        if cantidad_convertida > inventario.cantidad_disponible:
            messages.error(request, "La cantidad solicitada es mayor a la existente en Inventario.")
            return redirect('solicitar_recursos')

        # Registrar el uso del ítem
        uso_item = UsoItemLaboratorio(
            solicitud_id=solicitud_id,
            inventario=inventario,
            usuario_id=usuario_id,
            cantidad_utilizada=cantidad_utilizada_decimal,
            unidad_medida=unidad_medida,
            fecha_uso=fecha_uso,
            cantidad_disponible_momento=inventario.cantidad_disponible,
            unidad_medida_momento=inventario.unidad_medida,
        )
        uso_item.save()
        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')
        return redirect('solicitar_recursos')

    # Si es GET, cargar datos para la vista
    categorias = Categoria.objects.all()
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user, estado='pendiente')

    # Filtros avanzados
    fecha = request.GET.get('fecha')
    laboratorio = request.GET.get('laboratorio')

    # Obtener las solicitudes de recursos
    solicitudes_recursos = UsoItemLaboratorio.objects.filter(usuario=request.user)

    # Aplicar filtros
    if fecha:
        solicitudes_recursos = solicitudes_recursos.filter(fecha_uso=fecha)
    if laboratorio:
        solicitudes_recursos = solicitudes_recursos.filter(solicitud__laboratorio=laboratorio)

    # Ocultar solicitudes aprobadas antiguas (más de 30 días)
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual - timedelta(days=7)  # Mostrar solo las aprobadas en los últimos 30 días

    # Si el usuario no ha activado "mostrar historial completo", ocultar las aprobadas antiguas
    if request.GET.get('mostrar_historial') != 'true':
        solicitudes_recursos = solicitudes_recursos.exclude(fecha_uso__lt=fecha_limite)

    # Ordenar por fecha de uso (más recientes primero)
    solicitudes_recursos = solicitudes_recursos.order_by('-fecha_uso')

    # Paginación
    paginator = Paginator(solicitudes_recursos, 10)  # 10 solicitudes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Resumen de solicitudes
    solicitudes_pendientes = UsoItemLaboratorio.objects.filter(usuario=request.user, solicitud__estado='pendiente').count()
    solicitudes_aprobadas = UsoItemLaboratorio.objects.filter(usuario=request.user, solicitud__estado='aprobada').count()
    solicitudes_rechazadas = UsoItemLaboratorio.objects.filter(usuario=request.user, solicitud__estado='rechazada').count()

    # Laboratorios para el filtro
    laboratorios = SolicitudLaboratorio.objects.filter(usuario=request.user).values('laboratorio').distinct()

    return render(request, 'solicitar_recursos.html', {
        'solicitudes': solicitudes,
        'page_obj': page_obj,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'laboratorios': laboratorios,
        'categorias': categorias,
        'mostrar_historial': request.GET.get('mostrar_historial') == 'true',
    })

'''Después de groupby se construye un diccionario donde:
La clave (laboratorio) es el laboratorio asociado a la solicitud.
El valor es una lista de todas las solicitudes de recursos (items) que pertenecen a ese laboratorio.'''

# Vista para obtener las subcategorías de una categoría específica
@login_required
def obtener_subcategorias(request, categoria_id):
    subcategorias = SubCategoria.objects.filter(categoria_id=categoria_id).values('id_subcategoria', 'nombre')
    subcategorias_list = list(subcategorias)
    return JsonResponse({'subcategorias': subcategorias_list})

# Vista para obtener los ítems de una subcategoría específica dentro de una categoría
@login_required 
def obtener_items(request, categoria_id, subcategoria_id=None):
    try:
        # Validar que la categoría existe
        categoria = Categoria.objects.get(id_categoria=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({'error': 'Categoría no encontrada'}, status=404)
    
    if subcategoria_id:
        try:
            subcategoria = SubCategoria.objects.get(id_subcategoria=subcategoria_id, categoria_id=categoria_id)
            items = Inventario.objects.filter(categoria_id=categoria_id, subcategoria_id=subcategoria_id).values('id_inventario', 'nombre', 'descripcion', 'cantidad_disponible', 'unidad_medida')
        except SubCategoria.DoesNotExist:
            return JsonResponse({'error': 'Subcategoría no encontrada o no pertenece a la categoría'}, status=404)
    else:
        items = Inventario.objects.filter(categoria_id=categoria_id).values('id_inventario', 'nombre', 'descripcion', 'cantidad_disponible', 'unidad_medida')

    items_list = list(items)
    return JsonResponse({'items': items_list})

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
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, uso_item.inventario.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {uso_item.inventario.unidad_medida}.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        if cantidad_convertida > uso_item.inventario.cantidad_disponible:
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