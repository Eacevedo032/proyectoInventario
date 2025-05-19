from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from inventario_nuevo.forms import ProductoForm
from inventario_nuevo.models import UnidadMedida
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from decimal import Decimal, InvalidOperation
from inventario_nuevo.forms import CategoriaForm, SubcategoriaForm
from inventario_nuevo.models import Categoria, Subcategoria, Producto, Ubicacion, Lote, Medida,  BajaProducto
from inventario_nuevo.models import Marca, Modelo, Color, Presentacion, Capacidad, Accesorios, EstadoRecurso, UnidadMedida
from inventario_nuevo.forms import PresentacionForm, CapacidadForm, AccesoriosForm
from inventario_nuevo.forms import MarcaForm, ModeloForm, ColorForm, UbicacionForm, LoteForm, MedidaForm
from django.utils import timezone
from django.utils.timezone import localtime
from inventario_nuevo.models import HistorialInventario
from django.core.paginator import Paginator
from django.db.models import Q
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from inventario_nuevo.forms import ProductoEditForm
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from inventario_nuevo.utils import obtener_productos_filtrados
from datetime import datetime

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#Vista principal de agregar el producto
@login_required
@admin_required #Verifica si el usuario es administrador
def agregar_producto(request):
    form = ProductoForm()
    categoria_form = CategoriaForm()
    subcategoria_form = SubcategoriaForm()
    marca_form = MarcaForm()
    modelo_form = ModeloForm()
    color_form = ColorForm()
    capacidad_form = CapacidadForm() 
    presentacion_form = PresentacionForm() 
    accesorios_form = AccesoriosForm() 
    ubicacion_form = UbicacionForm()
    lote_form = LoteForm()
    medida_form = MedidaForm()
    
    if request.method == 'POST':
        form_tipo = request.POST.get('form_tipo')

        if form_tipo == 'categoria':
            categoria_form = CategoriaForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la categoría es obligatorio.")
            elif Categoria.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una categoría con el nombre '{nombre}'.")
            elif categoria_form.is_valid():
                categoria_form.save()
                messages.success(request, "Categoría agregada.")
                return redirect('agregar_producto')

        elif form_tipo == 'subcategoria':
            subcategoria_form = SubcategoriaForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la subcategoría es obligatorio.")
            elif Subcategoria.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una subcategoría con el nombre '{nombre}'.")
            elif subcategoria_form.is_valid():
                subcategoria_form.save()
                messages.success(request, "Subcategoría agregada.")
                return redirect('agregar_producto')

        elif form_tipo == 'marca':
            marca_form = MarcaForm(request.POST)
            if marca_form.is_valid():
                marca_form.save()
                messages.success(request, "Marca agregada.")
                return redirect('agregar_producto')
            else:
                for field, errors in marca_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'modelo':
            modelo_form = ModeloForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre del modelo es obligatorio.")
            elif Modelo.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe un modelo con el nombre '{nombre}'.")
            elif modelo_form.is_valid():
                modelo_form.save()
                messages.success(request, "Modelo agregado.")
                return redirect('agregar_producto')
            else:
                for field, errors in modelo_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'color':
            color_form = ColorForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre del color es obligatorio.")
            elif Color.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe un color con el nombre '{nombre}'.")
            elif color_form.is_valid():
                color_form.save()
                messages.success(request, "Color agregado.")
                return redirect('agregar_producto')
            else:
                for field, errors in color_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'capacidad': 
            capacidad_form = CapacidadForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la capacidad es obligatorio.")
            elif Capacidad.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una capacidad con el nombre '{nombre}'.")
            elif capacidad_form.is_valid():
                capacidad_form.save()
                messages.success(request, "Capacidad agregada.")
                return redirect('agregar_producto')
            else:
                for field, errors in capacidad_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'presentacion': 
            presentacion_form = PresentacionForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la presentación es obligatorio.")
            elif Capacidad.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una presentación con el nombre '{nombre}'.")
            elif presentacion_form.is_valid():
                presentacion_form.save()
                messages.success(request, "Presentación de Producto agregada.")
                return redirect('agregar_producto')
            else:
                for field, errors in presentacion_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'accesorios': 
            accesorios_form = AccesoriosForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre del Accesorio es obligatorio.")
            elif Accesorios.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe un Accesorio con el nombre '{nombre}'.")
            elif accesorios_form.is_valid():
                accesorios_form.save()
                messages.success(request, "Accesorios de Producto agregados.")
                return redirect('agregar_producto')
            else:
                for field, errors in accesorios_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'ubicacion':
            ubicacion_form = UbicacionForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la Ubicación es obligatorio.")
            elif Ubicacion.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una ubicación con el nombre '{nombre}'.")
            elif ubicacion_form.is_valid():
                ubicacion_form.save()
                messages.success(request, "Ubicación agregada con éxito.")
                return redirect('agregar_producto')
            else:
                for field, errors in ubicacion_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'lote':
            lote_form = LoteForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre del Lote es obligatorio.")
            elif Lote.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe un Lote con el Nombre '{nombre}'.")
            elif lote_form.is_valid():
                lote_form.save()
                messages.success(request, "Lote agregado correctamente.")
                return redirect('agregar_producto')
            else:
                for field, errors in lote_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)

        elif form_tipo == 'medida':
            medida_form = MedidaForm(request.POST)
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.warning(request, "El nombre de la Medida es obligatorio.")
            elif Medida.objects.filter(nombre__iexact=nombre).exists():
                messages.warning(request, f"Ya existe una Medida con el nombre '{nombre}'.")
            elif medida_form.is_valid():
                medida_form.save()
                messages.success(request, "Medida agregada correctamente.")
                return redirect('agregar_producto')
            else:
                for field, errors in medida_form.errors.items():
                    for error in errors:
                        messages.warning(request, error)
        
        elif form_tipo == 'producto':
            form = ProductoForm(request.POST or None)

    # Cargar subcategorías válidas antes de validar
    categoria_id = request.POST.get('categoria')
    if categoria_id:
        form.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id)

    if request.method == 'POST':
        if form.is_valid():
            producto = form.save(commit=False)

            # Asignar usuario actual
            producto.agregado_por = request.user

            # Validar que cantidad no sea negativa
            if producto.cantidad_disponible < 0:
                messages.error(request, "La cantidad disponible no puede ser negativa.")
                return render(request, 'inventario_nuevo/agregar_producto.html', {
                    'form': form,
                    'categoria_form': categoria_form,
                    'subcategoria_form': subcategoria_form,
                    'marca_form': marca_form,
                    'modelo_form': modelo_form,
                    'color_form': color_form,
                    'capacidad_form': capacidad_form,
                    'presentacion_form': presentacion_form,
                    'accesorios_form': accesorios_form,
                    'ubicacion_form': ubicacion_form,
                    'lote_form': lote_form,
                    'medida_form': medida_form,
                })

            # Validar unidad de medida
            try:
                cantidad_prueba = Decimal('1')
                unidad_destino = producto.unidad_medida
                convertir_usando_modelo(cantidad_prueba, unidad_destino, unidad_destino)
            except (ValueError, InvalidOperation) as e:
                messages.error(request, f"Error con la unidad de medida seleccionada: {e}")
                return render(request, 'inventario_nuevo/agregar_producto.html', {
                    'form': form,
                    'categoria_form': categoria_form,
                    'subcategoria_form': subcategoria_form,
                    'marca_form': marca_form,
                    'modelo_form': modelo_form,
                    'color_form': color_form,
                    'capacidad_form': capacidad_form,
                    'presentacion_form': presentacion_form,
                    'accesorios_form': accesorios_form,
                    'ubicacion_form': ubicacion_form,
                    'lote_form': lote_form,
                    'medida_form': medida_form,
                })

            producto.fecha_agregado = localtime(timezone.now()).date()
            producto.save()

            # CREAR EL HISTORIAL (PENDIENTEEEEEEE O SE ELIMINARÁ)
            HistorialInventario.objects.create(
                producto=producto,
                nombre_producto=producto.nombre,
                categoria=producto.categoria,
                subcategoria=producto.subcategoria,
                cantidad_inicial=producto.cantidad_disponible,
                unidad_medida=producto.unidad_medida,
                ubicacion_inicial=producto.ubicacion,
                estado_inicial=producto.estado,
                fecha_agregado=producto.fecha_agregado,
                agregado_por=producto.agregado_por,
                tipo_movimiento='ingreso_inicial'
            )

            messages.success(request, "Producto agregado correctamente.")
            return redirect('listar_productos')
        else:
            print(form.errors)  # para depurar errores silenciosos
            messages.error(request, "Formulario inválido. Verifica los campos.")
    
    return render(request, 'inventario_nuevo/agregar_producto.html', {
        'form': form,
        'categoria_form': categoria_form,
        'subcategoria_form': subcategoria_form,
        'marca_form': marca_form,
        'modelo_form': modelo_form,
        'color_form': color_form,
        'capacidad_form': capacidad_form,
        'presentacion_form': presentacion_form,
        'accesorios_form': accesorios_form,
        'ubicacion_form': ubicacion_form,
        'lote_form': lote_form,
        'medida_form': medida_form,
        'hoy': localtime(timezone.now()).date()
    })

@admin_required
def listar_productos(request):
    productos = Producto.objects.all().select_related(
        'categoria', 'subcategoria', 'marca', 'modelo', 'color', 'estado', 
        'ubicacion', 'lote', 'baja', 'presentacion'
    ).order_by('-fecha_agregado', '-id') #Esto muestra en orden del último agregado se muestra primero

    estado = request.GET.get('estado')
    if not estado or estado != 'baja':
        productos = productos.exclude(estado__estado='baja')

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

    filtros_aplicados = {}

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
        productos = productos.filter(num_serie__icontains=num_serie)
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

    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    context = {
        'productos': page_obj,
        'categorias': Categoria.objects.all(),
        'subcategorias': Subcategoria.objects.all(),
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'colores': Color.objects.all(),
        'presentaciones': Presentacion.objects.all(),  
        'estados': EstadoRecurso.objects.exclude(estado='prestado'),
        'ubicaciones': Ubicacion.objects.all(),
        'lotes': Lote.objects.all(),
        'total_resultados': productos.count(),
        'filtros_aplicados': filtros_aplicados,
        'params': params,
        'modo_baja': estado == 'baja',
    }

    #Estas banderas sirven para que la estructura mostrada en el HTML sea diferente por cada filtro aplicado
    context['filtro_por_presentacion'] = 'presentacion' in request.GET and request.GET['presentacion']
    context['filtro_por_color'] = 'color' in request.GET and request.GET['color']
    context['filtro_por_modelo'] = 'modelo' in request.GET and request.GET['modelo']
    context['filtro_por_marca'] = bool(request.GET.get('marca'))
    context['filtro_por_codigo'] = bool(request.GET.get('codigo'))
    context['filtro_por_num_cat'] = bool(request.GET.get('num_cat'))
    context['filtro_por_num_serie'] = bool(request.GET.get('num_serie'))

    return render(request, 'inventario_nuevo/listar_productos.html', context)

#Vista para Editar_Producto, usando el ProductoEditForm
@admin_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoEditForm(request.POST, instance=producto)

        # Precargar subcategorías según categoría seleccionada
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            form.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id)

        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{producto.nombre}' ha sido actualizado correctamente.")
            return redirect('listar_productos')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ProductoEditForm(instance=producto)

        # Precargar subcategorías si ya hay una categoría
        if producto.categoria:
            form.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria=producto.categoria)

    return render(request, 'inventario_nuevo/editar_producto.html', {
        'form': form,
        'producto': producto,
        'cantidad': producto.cantidad_disponible,  # La mostramos sin editar la cantidad
    })

@login_required
@admin_required
def dar_baja_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Verificar si ya fue dado de baja
    if BajaProducto.objects.filter(producto=producto).exists():
        messages.warning(request, "Este producto ya ha sido dado de baja.")
        return redirect('listar_productos')

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        foto = request.FILES.get('foto')

        if not motivo:
            messages.error(request, "Debe ingresar un motivo para la baja.")
        else:
            # Cambiar estado del producto a "baja"
            estado_baja = EstadoRecurso.objects.get(estado='baja')
            producto.estado = estado_baja
            producto.save()

            # Registrar la baja
            BajaProducto.objects.create(
                producto=producto,
                motivo=motivo,
                observaciones=observaciones,
                usuario=request.user,
                foto=foto
            )

            messages.success(request, f"El producto {producto.nombre} ha sido dado de baja correctamente.")
            return redirect('listar_productos')

    return render(request, 'inventario_nuevo/dar_baja_producto.html', {'producto': producto})

@login_required
@admin_required
def reporte_pdf_inventario(request):
    productos, filtros_aplicados = obtener_productos_filtrados(request)

    template_path = 'reportes/reporte_pdf_inventario.html'  # Desde la carpeta templates
    context = {
        'productos': productos,
        'filtros_aplicados': filtros_aplicados,
        'fecha_generacion': datetime.now(),
        'usuario': request.user,
        'total': productos.count()
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response
