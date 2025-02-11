from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import Categoria, Inventario, SolicitudLaboratorio, SubCategoria, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades

# Vista para solicitar recursos desde una cuenta de usuario sin privilegios de administrador
@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
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
            cantidad_utilizada_decimal = Decimal(cantidad_utilizada) #Convertimos la cantidad utilizada a decimal para que no haya conflicto entre datos
            if cantidad_utilizada_decimal <= 0:
                messages.error(request, "La cantidad a utilizar debe ser mayor a 0.")
                return redirect('solicitar_recursos')
        except (InvalidOperation, TypeError):
            messages.error(request, "La cantidad ingresada no es válida.")
            return redirect('solicitar_recursos')

        # Hacemos la conversión de la cantidad a la unidad del inventario para que tenga lógica
        try:
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, inventario.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {inventario.unidad_medida}. "
                                    "Solicite items cuyas unidades de medida tengan lógica con las medidas de Inventario.")
            return redirect('solicitar_recursos')
        
        # Verificamos si la cantidad solicitada es mayor que la disponible (cantidad ya convertida o no)
        if cantidad_convertida > inventario.cantidad_disponible:
            messages.error(request, "La cantidad solicitada es mayor a la existente en Inventario.")
            return redirect('solicitar_recursos')

        # Registrar el uso del ítem
        uso_item = UsoItemLaboratorio(
            solicitud_id=solicitud_id,
            inventario=inventario,
            usuario_id=usuario_id,
            cantidad_utilizada=cantidad_utilizada_decimal,  #Acá le pasamos la cantidad correcta luego de hacer conversiones y validaciones
            unidad_medida=unidad_medida,
            fecha_uso=fecha_uso,
            cantidad_disponible_momento=inventario.cantidad_disponible, #Estas de momento, obtienen y guardan la cantidad hasta la fecha solicitada (con el objetivo de mostrarla solo)
            unidad_medida_momento=inventario.unidad_medida,
        )
        uso_item.save()
        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')
        return redirect('solicitar_recursos')

    # Si es GET, cargar datos para la vista
    categorias = Categoria.objects.all()
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)
    solicitudes_recursos = UsoItemLaboratorio.objects.filter(usuario=request.user).select_related('inventario', 'solicitud').order_by('solicitud__laboratorio')

    solicitudes_por_laboratorio = {
        laboratorio: list(items)
        for laboratorio, items in groupby(solicitudes_recursos, key=lambda x: x.solicitud.laboratorio) #groupby es una función de itertools que requiere que los datos estén ordenados previamente.
    }

    return render(request, 'solicitar_recursos.html', {
        'solicitudes': solicitudes,
        'solicitudes_por_laboratorio': solicitudes_por_laboratorio,
        'categorias': categorias
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