from django.shortcuts import render
from inventario_nuevo.models import UnidadMedida
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Categoria, Producto
from inventario_nuevo.models import EstadoRecurso, UnidadMedida

# Vista para filtrar los estados de un Productos
def filtrar_por_estados(request):
    estados = EstadoRecurso.objects.all()
    productos = Producto.objects.select_related(
        'categoria', 'subcategoria', 'unidad_medida', 'ubicacion'
    )

    ver_todos = request.GET.get("ver_todos") == "1"
    estados_seleccionados = request.GET.getlist("estados")

    # Evita mostrar productos si no hay filtros aplicados
    if not estados_seleccionados and not ver_todos:
        return render(request, 'inventario_nuevo/filtrar_por_estado.html', {
            'todos_estados': estados,
            'productos_por_estado': {},  # Nada para mostrar
            'estados_seleccionados': [],
            'ver_todos': False,
            'categorias': Categoria.objects.prefetch_related('subcategoria_set'),
        })

    if ver_todos:
        productos_filtrados = productos
    else:
        productos_filtrados = productos.filter(estado__in=estados_seleccionados)

    # Agrupar por estado
    productos_por_estado = {}
    for producto in productos_filtrados:
        productos_por_estado.setdefault(producto.estado, []).append(producto)

    context = {
        'todos_estados': estados,
        'productos_por_estado': productos_por_estado,
        'estados_seleccionados': [int(e) for e in estados_seleccionados],
        'ver_todos': ver_todos,
        'categorias': Categoria.objects.prefetch_related('subcategoria_set'),
    }

    return render(request, 'inventario_nuevo/filtrar_por_estado.html', context)

#Filtrar Productos por unidades
def filtrar_por_unidades(request):
    unidades = UnidadMedida.objects.all()
    productos = Producto.objects.select_related(
        'categoria', 'subcategoria', 'unidad_medida', 'ubicacion'
    )

    ver_todos = request.GET.get("ver_todos") == "1"
    unidades_seleccionadas = request.GET.getlist("unidades")

    if not unidades_seleccionadas and not ver_todos:
        return render(request, 'inventario_nuevo/filtrar_por_unidad.html', {
            'todas_unidades': unidades,
            'productos_por_unidad': {},
            'unidades_seleccionadas': [],
            'ver_todos': False,
            'categorias': Categoria.objects.prefetch_related('subcategoria_set'),
        })

    if ver_todos:
        productos_filtrados = productos
    else:
        productos_filtrados = productos.filter(unidad_medida__id__in=unidades_seleccionadas)

    # Agrupar por unidad de medida
    productos_por_unidad = {}
    for producto in productos_filtrados:
        productos_por_unidad.setdefault(producto.unidad_medida, []).append(producto)

    context = {
        'todas_unidades': unidades,
        'productos_por_unidad': productos_por_unidad,
        'unidades_seleccionadas': [int(u) for u in unidades_seleccionadas],
        'ver_todos': ver_todos,
        'categorias': Categoria.objects.prefetch_related('subcategoria_set'),
    }

    return render(request, 'inventario_nuevo/filtrar_por_unidad.html', context)
