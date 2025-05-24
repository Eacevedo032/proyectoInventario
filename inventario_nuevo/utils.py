# inventario/utils.py

from .models import Producto, Categoria, Subcategoria, Marca, Modelo, Color, EstadoRecurso, Ubicacion, Lote, Presentacion, BajaProducto

def obtener_productos_filtrados(request):
    estado = request.GET.get('estado')
    mostrar_bajas = estado == 'baja'
    filtros_aplicados = {}
    filtros_usados = set()

    if mostrar_bajas:
        productos = BajaProducto.objects.select_related(
            'producto__categoria', 'producto__subcategoria', 'producto__marca',
            'producto__modelo', 'producto__color', 'producto__ubicacion',
            'producto__lote', 'producto__presentacion', 'producto__estado',
            'usuario', 'producto__unidad_medida'
        ).order_by('-fecha_baja')
    else:
        productos = Producto.objects.select_related(
            'categoria', 'subcategoria', 'marca', 'modelo', 'color', 'estado',
            'ubicacion', 'lote', 'presentacion', 'unidad_medida'
        ).exclude(estado__estado='baja').order_by('-fecha_agregado', '-id')

    def aplicar_filtro(campo, lookup, modelo=None, relacion=False):
        nonlocal productos
        valor = request.GET.get(campo)
        if valor:
            filtros_usados.add(campo)
            if relacion and modelo:
                try:
                    obj = modelo.objects.get(id=valor)
                    filtros_aplicados[campo.capitalize()] = obj.nombre
                except modelo.DoesNotExist:
                    return
            else:
                filtros_aplicados[campo.replace('_', ' ').capitalize()] = valor
            productos = productos.filter(**{lookup: valor})

    def aplicar_filtro_fecha(nombre_display, campo_db):
        nonlocal productos
        desde = request.GET.get(f'{campo_db}_desde')
        hasta = request.GET.get(f'{campo_db}_hasta')
        if desde and hasta:
            productos = productos.filter(**{f'{campo_db}__range': [desde, hasta]})
            filtros_aplicados[nombre_display] = f"{desde} a {hasta}"
        elif desde:
            productos = productos.filter(**{f'{campo_db}__gte': desde})
            filtros_aplicados[f'{nombre_display} desde'] = desde
        elif hasta:
            productos = productos.filter(**{f'{campo_db}__lte': hasta})
            filtros_aplicados[f'{nombre_display} hasta'] = hasta

    campos_texto = ['nombre', 'codigo', 'num_cat', 'num_serie']
    relaciones = {
        'categoria': Categoria,
        'subcategoria': Subcategoria,
        'marca': Marca,
        'modelo': Modelo,
        'color': Color,
        'presentacion': Presentacion,
        'ubicacion': Ubicacion,
        'lote': Lote,
    }

    for campo in campos_texto:
        lookup = f'producto__{campo}__icontains' if mostrar_bajas else f'{campo}__icontains'
        aplicar_filtro(campo, lookup)

    for campo, modelo in relaciones.items():
        path = f'producto__{campo}' if mostrar_bajas else campo
        lookup = f'{path}_id'
        aplicar_filtro(campo, lookup, modelo, relacion=True)

    # Filtro por estado (solo productos activos, no en bajas)
    if not mostrar_bajas and estado in ['disponible', 'no_disponible']:
        estado_obj = EstadoRecurso.objects.filter(estado=estado).first()
        if estado_obj:
            productos = productos.filter(estado=estado_obj)
            filtros_aplicados['Estado'] = estado_obj.get_estado_display()

    # Fechas
    aplicar_filtro_fecha('Fecha agregado', 'producto__fecha_agregado' if mostrar_bajas else 'fecha_agregado')
    aplicar_filtro_fecha('Vencimiento', 'producto__vencimiento' if mostrar_bajas else 'vencimiento')

    return productos, filtros_aplicados, mostrar_bajas
