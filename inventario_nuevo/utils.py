# inventario/utils.py

from .models import Producto, Categoria, Subcategoria, Marca, Modelo, Color, EstadoRecurso, Ubicacion, Lote, Presentacion

def obtener_productos_filtrados(request):
    productos = Producto.objects.all().select_related(
        'categoria', 'subcategoria', 'marca', 'modelo', 'color',
        'estado', 'ubicacion', 'lote', 'baja', 'presentacion'
    ).order_by('-fecha_agregado', '-id')

    estado = request.GET.get('estado')
    if not estado or estado != 'baja':
        productos = productos.exclude(estado__estado='baja')

    filtros_aplicados = {}
    nombre = request.GET.get('nombre')
    codigo = request.GET.get('codigo')
    num_cat = request.GET.get('num_cat')
    num_serie = request.GET.get('num_serie')
    categoria = request.GET.get('categoria')
    subcategoria = request.GET.get('subcategoria')
    marca = request.GET.get('marca')
    modelo = request.GET.get('modelo')
    color = request.GET.get('color')
    presentacion = request.GET.get('presentacion')
    ubicacion = request.GET.get('ubicacion')
    lote = request.GET.get('lote')
    fecha_agregado_desde = request.GET.get('fecha_agregado_desde')
    fecha_agregado_hasta = request.GET.get('fecha_agregado_hasta')
    vencimiento_desde = request.GET.get('vencimiento_desde')
    vencimiento_hasta = request.GET.get('vencimiento_hasta')

    if nombre:
        productos = productos.filter(nombre__icontains=nombre)
        filtros_aplicados['Nombre'] = nombre
    if codigo:
        productos = productos.filter(codigo__icontains=codigo)
        filtros_aplicados['Código'] = codigo
    if num_cat:
        productos = productos.filter(num_cat__icontains=num_cat)
        filtros_aplicados['N° de Catálogo'] = num_cat
    if num_serie:
        productos = productos.filter(numero_serie__icontains=num_serie)
        filtros_aplicados['N° de Serie'] = num_serie
    if categoria:
        try:
            cat = Categoria.objects.get(id=categoria)
            productos = productos.filter(categoria_id=categoria)
            filtros_aplicados['Categoría'] = cat.nombre
        except Categoria.DoesNotExist:
            pass
    if subcategoria:
        try:
            subcat = Subcategoria.objects.get(id=subcategoria)
            productos = productos.filter(subcategoria_id=subcategoria)
            filtros_aplicados['Subcategoría'] = subcat.nombre
        except Subcategoria.DoesNotExist:
            pass
    if marca:
        try:
            mar = Marca.objects.get(id=marca)
            productos = productos.filter(marca_id=marca)
            filtros_aplicados['Marca'] = mar.nombre
        except Marca.DoesNotExist:
            pass
    if modelo:
        try:
            mod = Modelo.objects.get(id=modelo)
            productos = productos.filter(modelo_id=modelo)
            filtros_aplicados['Modelo'] = mod.nombre
        except Modelo.DoesNotExist:
            pass
    if color:
        try:
            col = Color.objects.get(id=color)
            productos = productos.filter(color_id=color)
            filtros_aplicados['Color'] = col.nombre
        except Color.DoesNotExist:
            pass
    if presentacion:
        try:
            pres = Presentacion.objects.get(id=presentacion)
            productos = productos.filter(presentacion_id=presentacion)
            filtros_aplicados['Presentación'] = pres.nombre
        except Presentacion.DoesNotExist:
            pass
    if estado:
        estado_obj = EstadoRecurso.objects.filter(estado=estado).first()
        if estado_obj:
            productos = productos.filter(estado=estado_obj)
            filtros_aplicados['Estado'] = estado_obj.get_estado_display()
    if ubicacion:
        try:
            ubi = Ubicacion.objects.get(id=ubicacion)
            productos = productos.filter(ubicacion_id=ubicacion)
            filtros_aplicados['Ubicación'] = ubi.nombre
        except Ubicacion.DoesNotExist:
            pass
    if lote:
        try:
            lot = Lote.objects.get(id=lote)
            productos = productos.filter(lote_id=lote)
            filtros_aplicados['Lote'] = lot.nombre
        except Lote.DoesNotExist:
            pass

    if fecha_agregado_desde and fecha_agregado_hasta:
        productos = productos.filter(fecha_agregado__range=[fecha_agregado_desde, fecha_agregado_hasta])
        filtros_aplicados['Fecha de agregado'] = f"{fecha_agregado_desde} a {fecha_agregado_hasta}"
    elif fecha_agregado_desde:
        productos = productos.filter(fecha_agregado__gte=fecha_agregado_desde)
        filtros_aplicados['Fecha de agregado desde'] = fecha_agregado_desde
    elif fecha_agregado_hasta:
        productos = productos.filter(fecha_agregado__lte=fecha_agregado_hasta)
        filtros_aplicados['Fecha de agregado hasta'] = fecha_agregado_hasta

    if vencimiento_desde and vencimiento_hasta:
        productos = productos.filter(vencimiento__range=[vencimiento_desde, vencimiento_hasta])
        filtros_aplicados['Fecha de vencimiento'] = f"{vencimiento_desde} a {vencimiento_hasta}"
    elif vencimiento_desde:
        productos = productos.filter(vencimiento__gte=vencimiento_desde)
        filtros_aplicados['Vencimiento desde'] = vencimiento_desde
    elif vencimiento_hasta:
        productos = productos.filter(vencimiento__lte=vencimiento_hasta)
        filtros_aplicados['Vencimiento hasta'] = vencimiento_hasta

    return productos, filtros_aplicados
