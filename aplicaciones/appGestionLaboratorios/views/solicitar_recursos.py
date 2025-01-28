from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import Categoria, Inventario, SolicitudLaboratorio, SubCategoria, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date

# Vista para solicitar recursos desde una cuenta de usuario sin privilegios de administrador
@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        inventario_id = request.POST.get('inventario')  # Cambiado a 'inventario'
        usuario_id = request.POST.get('usuario')
        cantidad_utilizada = request.POST.get('cantidad_utilizada')
        fecha_uso = request.POST.get('fecha_uso')

        # Crear instancia de UsoItemLaboratorio
        uso_item = UsoItemLaboratorio(
            solicitud_id=solicitud_id,
            inventario_id=inventario_id,  # Cambiado a 'inventario_id'
            usuario_id=usuario_id,
            cantidad_utilizada=cantidad_utilizada,
            fecha_uso=fecha_uso
        )
        uso_item.save()
        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')
        return redirect('solicitar_recursos')

    categorias = Categoria.objects.all()
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    solicitudes_recursos = UsoItemLaboratorio.objects.filter(
        usuario=request.user
    ).select_related('inventario', 'solicitud').order_by('solicitud__laboratorio')

    solicitudes_por_laboratorio = {
        laboratorio: list(items)
        for laboratorio, items in groupby(solicitudes_recursos, key=lambda x: x.solicitud.laboratorio)
    }

    return render(request, 'solicitar_recursos.html', {
        'solicitudes': solicitudes,
        'solicitudes_por_laboratorio': solicitudes_por_laboratorio,
        'categorias': categorias
    })

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