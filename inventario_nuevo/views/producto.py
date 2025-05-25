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
from datetime import datetime, date
from weasyprint import HTML
from django.templatetags.static import static
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import datetime as dt
from openpyxl import Workbook
from django.http import HttpResponse
from weasyprint import HTML
import tempfile
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from django.utils import timezone
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

            # Asignar el estado 'disponible' automáticamente
            estado_disponible = EstadoRecurso.objects.filter(estado='disponible').first()
            producto.estado = estado_disponible

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
    estado = request.GET.get('estado')
    mostrar_bajas = estado == 'baja'

    filtros_aplicados = {}
    filtros_booleans = {}
    filtros_activos = 0
    advertencia_bajas = None

    if mostrar_bajas:
        filtros_aplicados['Estado'] = 'Dado de baja'
        filtros_booleans['filtro_por_estado'] = True
        filtros_activos += 1

    if mostrar_bajas:
        queryset = BajaProducto.objects.select_related(
            'producto__categoria', 'producto__subcategoria', 'producto__marca',
            'producto__modelo', 'producto__color', 'producto__ubicacion',
            'producto__lote', 'producto__presentacion', 'producto__estado',
            'usuario', 'producto__unidad_medida'
        ).order_by('-fecha_baja')
    else:
        queryset = Producto.objects.select_related(
            'categoria', 'subcategoria', 'marca', 'modelo', 'color', 'estado',
            'ubicacion', 'lote', 'presentacion', 'unidad_medida'
        ).exclude(estado__estado='baja').order_by('-fecha_agregado', '-id')

    filtros_usados_modo_baja = set()
    filtros_permitidos_modo_baja = {'nombre', 'categoria', 'subcategoria'}

    def aplicar_filtro_texto(campo, lookup):
        nonlocal queryset, filtros_activos, filtros_usados_modo_baja
        valor = request.GET.get(campo)
        if valor:
            if mostrar_bajas:
                filtros_usados_modo_baja.add(campo)
            lookup_dict = {lookup: valor}
            queryset = queryset.filter(**lookup_dict)
            filtros_aplicados[campo.replace('_', ' ').capitalize()] = valor
            filtros_booleans[f'filtro_por_{campo}'] = True
            filtros_activos += 1
        else:
            filtros_booleans[f'filtro_por_{campo}'] = False

    def aplicar_filtro_relacion(campo, modelo, path=None):
        nonlocal queryset, filtros_activos, filtros_usados_modo_baja
        valor = request.GET.get(campo)
        if valor:
            try:
                obj = modelo.objects.get(id=valor)
                if mostrar_bajas:
                    filtros_usados_modo_baja.add(campo)
                lookup = f'{path}_id'
                queryset = queryset.filter(**{lookup: valor})
                filtros_aplicados[campo.capitalize()] = obj.nombre
                filtros_booleans[f'filtro_por_{campo}'] = True
                filtros_activos += 1
            except modelo.DoesNotExist:
                filtros_booleans[f'filtro_por_{campo}'] = False
        else:
            filtros_booleans[f'filtro_por_{campo}'] = False

    def aplicar_filtro_fecha(nombre_display, campo_db):
        nonlocal queryset, filtros_activos
        if mostrar_bajas:
            return  # No aplicar filtros por fecha en modo baja
        desde = request.GET.get(f'{campo_db}_desde')
        hasta = request.GET.get(f'{campo_db}_hasta')
        if desde and hasta:
            queryset = queryset.filter(**{f'{campo_db}__range': [desde, hasta]})
            filtros_aplicados[nombre_display] = f"{desde} a {hasta}"
            filtros_activos += 1
        elif desde:
            queryset = queryset.filter(**{f'{campo_db}__gte': desde})
            filtros_aplicados[f'{nombre_display} desde'] = desde
            filtros_activos += 1
        elif hasta:
            queryset = queryset.filter(**{f'{campo_db}__lte': hasta})
            filtros_aplicados[f'{nombre_display} hasta'] = hasta
            filtros_activos += 1

    # Filtros de texto
    for campo in ['nombre', 'codigo', 'num_cat', 'num_serie']:
        path = f'producto__{campo}' if mostrar_bajas else campo
        aplicar_filtro_texto(campo, f'{path}__icontains')

    # Filtros de relaciones
    relaciones = {
        'categoria': Categoria,
        'subcategoria': Subcategoria,
        'marca': Marca,
        'modelo': Modelo,
        'color': Color,
        'presentacion': Presentacion,
        'ubicacion': Ubicacion,
        'lote': Lote,
        'unidad_medida': UnidadMedida,
    }
    for campo, modelo in relaciones.items():
        path = f'producto__{campo}' if mostrar_bajas else campo
        aplicar_filtro_relacion(campo, modelo, path)

    # Filtro de estado (solo para productos activos)
    if not mostrar_bajas and estado in ['disponible', 'no_disponible']:
        estado_obj = EstadoRecurso.objects.filter(estado=estado).first()
        if estado_obj:
            queryset = queryset.filter(estado=estado_obj)
            filtros_aplicados['Estado'] = estado_obj.get_estado_display()
            filtros_booleans['filtro_por_estado'] = True
            filtros_activos += 1

    # Filtros por fechas (solo en productos activos)
    aplicar_filtro_fecha('Fecha agregado', 'producto__fecha_agregado' if mostrar_bajas else 'fecha_agregado')
    aplicar_filtro_fecha('Vencimiento', 'producto__vencimiento' if mostrar_bajas else 'vencimiento')

    if mostrar_bajas:
        filtros_no_permitidos = filtros_usados_modo_baja - filtros_permitidos_modo_baja
        if filtros_no_permitidos:
            advertencia_bajas = (
                "⚠️ Solo se permite filtrar por nombre, categoría y subcategoría cuando se consultan productos dados de baja. "
                "Los filtros adicionales han sido ignorados."
            )

    # Paginación
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if 'page' in params:
        params.pop('page')

    context = {
        'productos': page_obj,
        'bajas': page_obj if mostrar_bajas else None,
        'mostrando_bajas': mostrar_bajas,
        'modo_baja': mostrar_bajas,
        'total_resultados': queryset.count(),
        'filtros_aplicados': filtros_aplicados,
        'filtros_combinados': filtros_activos > 1,
        'mensaje_advertencia': advertencia_bajas,
        'params': params,
        'categorias': Categoria.objects.all(),
        'subcategorias': Subcategoria.objects.all(),
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'colores': Color.objects.all(),
        'presentaciones': Presentacion.objects.all(),
        'estados': EstadoRecurso.objects.exclude(estado='prestado'),
        'ubicaciones': Ubicacion.objects.all(),
        'lotes': Lote.objects.all(),
        'unidades_medida': UnidadMedida.objects.all(),
    }
    context.update(filtros_booleans)

    return render(request, 'inventario_nuevo/listar_productos.html', context)

@admin_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    bajas_previas = BajaProducto.objects.filter(producto=producto).exists()
    estado_no_disponible = EstadoRecurso.objects.filter(estado='no disponible').first()
    estado_baja = EstadoRecurso.objects.filter(estado='baja').first()

    if request.method == 'POST':
        form = ProductoEditForm(request.POST, instance=producto)

        # Precargar subcategorías según categoría seleccionada
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            form.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id)

        if form.is_valid():
            producto_editado = form.save(commit=False)
            nueva_cantidad = producto_editado.cantidad_disponible

            # Lógica de protección contra baja automática
            if nueva_cantidad == 0:
                if bajas_previas:
                    # No permitir baja automática si ya hubo bajas previas
                    if estado_no_disponible:
                        producto_editado.estado = estado_no_disponible
                else:
                    # Si nunca ha tenido bajas, puede quedar en "baja" si se decide
                    # Aquí no hacemos nada, el estado permanece según selección del usuario
                    pass

            producto_editado.save()
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
        'cantidad': producto.cantidad_disponible,
    })

#Dar de baja al producto
@login_required
@admin_required
def dar_baja_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        foto = request.FILES.get('foto')

        # Caso 1: Hay unidades disponibles
        if producto.cantidad_disponible > 0:
            cantidad_str = request.POST.get('cantidad', '').strip()

            try:
                cantidad = Decimal(cantidad_str)
            except:
                messages.error(request, "La cantidad ingresada no es válida.")
                return redirect('dar_baja_producto', producto_id=producto.id)

            if cantidad <= 0:
                messages.error(request, "La cantidad debe ser mayor a 0.")
            elif cantidad > producto.cantidad_disponible:
                messages.error(request, f"No puedes dar de baja más de {producto.cantidad_disponible} unidades.")
            elif not motivo:
                messages.error(request, "Debe ingresar un motivo para la baja.")
            else:
                # Registrar baja parcial
                BajaProducto.objects.create(
                    producto=producto,
                    cantidad=cantidad,
                    motivo=motivo,
                    observaciones=observaciones,
                    usuario=request.user,
                    foto=foto
                )

                producto.cantidad_disponible -= cantidad
                # Determinar estado según la nueva cantidad
                if producto.cantidad_disponible == 0:
                    estado_no_disp = EstadoRecurso.objects.filter(estado='no_disponible').first()
                    if estado_no_disp:
                        producto.estado = estado_no_disp
                producto.save()

                messages.success(request, f"{cantidad} unidades del producto {producto.nombre} han sido dadas de baja.")
                return redirect('listar_productos')

        else:
            # Producto ya sin unidades -> Baja definitiva
            if not motivo:
                messages.error(request, "Debe ingresar un motivo para la baja.")
            else:
                BajaProducto.objects.create(
                    producto=producto,
                    cantidad=0,
                    motivo=motivo,
                    observaciones=observaciones,
                    usuario=request.user,
                    foto=foto
                )

                estado_baja = EstadoRecurso.objects.filter(estado='baja').first()
                if estado_baja:
                    producto.estado = estado_baja
                producto.save()

                messages.success(request, f"El producto {producto.nombre} ha sido dado de baja definitivamente.")
                return redirect('listar_productos')

    return render(request, 'inventario_nuevo/dar_baja_producto.html', {
        'producto': producto
    })
# REPORTES
@login_required
@admin_required
def vista_reporte_inventario(request):
    estado = request.GET.get('estado')
    mostrar_bajas = estado == 'baja'
    
    # Lista de posibles campos de filtro
    campos_filtro = [
        'categoria', 'subcategoria', 'marca', 'modelo', 'color',
        'estado', 'presentacion', 'ubicacion', 'lote',
        'nombre', 'codigo', 'num_cat', 'num_serie', 'bajas',
    ]

    # Banderas por cada filtro específico
    context = {
        'categorias': Categoria.objects.all(),
        'subcategorias': Subcategoria.objects.all(),
        'marcas': Marca.objects.all(),
        'modelos': Modelo.objects.all(),
        'colores': Color.objects.all(),
        'presentaciones': Presentacion.objects.all(),
        'estados': EstadoRecurso.objects.exclude(estado='prestado'),
        'ubicaciones': Ubicacion.objects.all(),
        'lotes': Lote.objects.all(),

        'filtro_por_presentacion': 'presentacion' in request.GET and request.GET['presentacion'],
        'filtro_por_color': 'color' in request.GET and request.GET['color'],
        'filtro_por_modelo': 'modelo' in request.GET and request.GET['modelo'],
        'filtro_por_marca': bool(request.GET.get('marca')),
        'filtro_por_codigo': bool(request.GET.get('codigo')),
        'filtro_por_num_cat': bool(request.GET.get('num_cat')),
        'filtro_por_num_serie': bool(request.GET.get('num_serie')),
    }

    # Contar cuántos filtros están siendo aplicados
    filtros_activos = sum(1 for campo in campos_filtro if request.GET.get(campo))
    context['filtros_combinados'] = filtros_activos > 1

    return render(request, 'reportes/vista_reporte_inventario.html', context)

@admin_required
def reporte_pdf_inventario(request):
    # Obtener productos filtrados y filtros aplicados
    productos, filtros_aplicados, es_modo_baja = obtener_productos_filtrados(request)

    # Construcción de URL absoluta para el logo
    logo_url = request.build_absolute_uri(static('img/logoUNP1.png'))

    # Definición de campos posibles de filtro
    campos_filtro = [
        'categoria', 'subcategoria', 'marca', 'modelo', 'color',
        'estado', 'presentacion', 'ubicacion', 'lote',
        'nombre', 'codigo', 'num_cat', 'num_serie',
        'fecha_agregado_desde', 'fecha_agregado_hasta',
        'vencimiento_desde', 'vencimiento_hasta'
    ]
    filtros_activos = sum(bool(request.GET.get(campo)) for campo in campos_filtro)

    # Contexto del template
    context = {
        'productos': productos,
        'filtros_aplicados': filtros_aplicados,
        'fecha_generacion': timezone.now(),
        'usuario': request.user,
        'total': productos.count(),
        'logo_url': logo_url,

        # Indicadores de columnas a mostrar (según filtros activos)
        'filtro_por_presentacion': bool(request.GET.get('presentacion')),
        'filtro_por_color': bool(request.GET.get('color')),
        'filtro_por_modelo': bool(request.GET.get('modelo')),
        'filtro_por_marca': bool(request.GET.get('marca')),
        'filtro_por_codigo': bool(request.GET.get('codigo')),
        'filtro_por_num_cat': bool(request.GET.get('num_cat')),
        'filtro_por_num_serie': bool(request.GET.get('num_serie')),
        'filtro_por_lote': bool(request.GET.get('lote')),
        'filtro_por_fecha_agregado': bool(request.GET.get('fecha_agregado_desde') or request.GET.get('fecha_agregado_hasta')),
        'filtro_por_vencimiento': bool(request.GET.get('vencimiento_desde') or request.GET.get('vencimiento_hasta')),
        'filtros_combinados': filtros_activos > 1
    }

    # Renderizado del PDF
    template = get_template('reportes/reporte_pdf_inventario.html')
    html_string = template.render(context)
    pdf_file = HTML(string=html_string).write_pdf()

    # Preparar respuesta HTTP con PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f'reporte_inventario_{fecha_actual}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    return response

#Para el reporte Excel, que se genera gracias a la librería openpyxl

from openpyxl.utils import get_column_letter

@admin_required
def reporte_excel_inventario(request):
    productos = Producto.objects.select_related(
        'unidad_medida', 'categoria', 'subcategoria', 'marca', 'modelo',
        'color', 'presentacion', 'ubicacion', 'lote', 'estado', 'agregado_por'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"

    # --- ESTILOS ---
    encabezado_font = Font(bold=True, color="FFFFFF")
    encabezado_fill = PatternFill(start_color="0000FF", end_color="0000FF", fill_type="solid")
    alineacion_centro = Alignment(horizontal='center', vertical='center')
    alineacion_izquierda = Alignment(horizontal='left', vertical='top', wrapText=True)
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # --- HOJA 1: INVENTARIO ACTIVO ---
    columnas = [
        ('Productos', 'nombre'),
        ('Cantidad', 'cantidad_disponible'),
        ('Unidad', 'unidad_medida.nombre'),
        ('Código', 'codigo'),
        ('N° Catálogo', 'num_cat'),
        ('N° Serie', 'num_serie'),
        ('Categoría', 'categoria.nombre'),
        ('Subcategoría', 'subcategoria.nombre'),
        ('Marca', 'marca.nombre'),
        ('Modelo', 'modelo.nombre'),
        ('Color', 'color.nombre'),
        ('Presentación', 'presentacion.nombre'),
        ('Ubicación', 'ubicacion.nombre'),
        ('Lote', 'lote.nombre'),
        ('Estado', 'estado.estado'),
        ('Fecha agregado', 'fecha_agregado'),
        ('Vencimiento', 'vencimiento'),
        ('Descripción', 'descripcion'),
        ('Accesorios', 'accesorios'),
        ('Capacidad', 'capacidad'),
        ('Medida', 'medida'),
        ('Observaciones', 'observacion'),
        ('Usuario que agrega', 'agregado_por.username'),
    ]

    # Título principal
    ws.insert_rows(1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columnas))
    titulo_cell = ws.cell(row=1, column=1, value="REPORTE DE INVENTARIO GENERAL")
    titulo_cell.font = Font(bold=True, size=14)
    titulo_cell.alignment = Alignment(horizontal='center')

    # Encabezados
    for col_idx, (titulo, _) in enumerate(columnas, start=1):
        cell = ws.cell(row=2, column=col_idx, value=titulo)
        cell.font = encabezado_font
        cell.fill = encabezado_fill
        cell.alignment = alineacion_centro
        cell.border = thin_border

    # Filas de datos
    for fila, producto in enumerate(productos, start=3):
        for col_idx, (titulo, atributo) in enumerate(columnas, start=1):
            partes = atributo.split('.')
            valor = producto
            try:
                for parte in partes:
                    if valor is None:
                        break
                    valor = getattr(valor, parte, None)
            except AttributeError:
                valor = ''
            if isinstance(valor, (datetime, date)):
                valor = valor.strftime('%d/%m/%Y')
            elif valor is None:
                valor = ''
            elif not isinstance(valor, (str, int, float, bool)):
                valor = str(valor)

            cell = ws.cell(row=fila, column=col_idx, value=valor)

            if titulo in ['Productos', 'Presentación', 'Observaciones', 'Descripción']:
                cell.alignment = alineacion_izquierda
            else:
                cell.alignment = alineacion_centro

            cell.border = thin_border

    # Ajuste de anchos
    for i, column_cells in enumerate(ws.columns, start=1):
        col_letter = get_column_letter(i)
        encabezado = ws.cell(row=2, column=i).value
        if encabezado in ['Productos', 'Presentación', 'Observaciones', 'Descripción']:
            ws.column_dimensions[col_letter].width = 30
        else:
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in column_cells)
            ws.column_dimensions[col_letter].width = max(15, max_length + 2)

    # --- HOJA 2: DADOS DE BAJA ---
    ws_baja = wb.create_sheet(title="Dados de baja")

    columnas_baja = [
        ('Productos', 'producto.nombre'),
        ('Categoría', 'producto.categoria.nombre'),
        ('Subcategoría', 'producto.subcategoria.nombre'),
        ('Cantidad', 'producto.cantidad_disponible'),
        ('Unidad', 'producto.unidad_medida.nombre'),
        ('Fecha baja', 'fecha_baja'),
        ('Motivo', 'motivo'),
        ('Observaciones', 'observaciones'),
        ('Usuario dió baja', 'usuario.username'),
    ]

    # Título principal
    ws_baja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columnas_baja))
    titulo_baja = ws_baja.cell(row=1, column=1)
    titulo_baja.value = "REPORTE DE PRODUCTOS DADOS DE BAJA"
    titulo_baja.font = Font(size=14,bold=True, color="FFFFFF")
    titulo_baja.alignment = Alignment(horizontal='center', vertical='center')
    titulo_baja.fill = encabezado_fill

    # Encabezados fila 2
    for col_idx, (titulo, _) in enumerate(columnas_baja, start=1):
        cell = ws_baja.cell(row=2, column=col_idx, value=titulo)
        cell.font = encabezado_font
        cell.fill = encabezado_fill
        cell.alignment = alineacion_centro
        cell.border = thin_border

    # Datos desde fila 3
    productos_baja = BajaProducto.objects.select_related(
        'producto__categoria', 'producto__subcategoria',
        'producto__unidad_medida', 'usuario'
    )

    for fila, baja in enumerate(productos_baja, start=3):
        for col_idx, (_, atributo) in enumerate(columnas_baja, start=1):
            partes = atributo.split('.')
            valor = baja
            try:
                for parte in partes:
                    if valor is None:
                        break
                    valor = getattr(valor, parte, None)
            except AttributeError:
                valor = ''
            if isinstance(valor, (datetime, date)):
                valor = valor.strftime('%d/%m/%Y')
            elif valor is None:
                valor = ''
            elif not isinstance(valor, (str, int, float, bool)):
                valor = str(valor)

            cell = ws_baja.cell(row=fila, column=col_idx, value=valor)

            if columnas_baja[col_idx - 1][0] in ['Productos', 'Motivo', 'Observaciones']:
                cell.alignment = alineacion_izquierda
            else:
                cell.alignment = alineacion_centro

            cell.border = thin_border

    # Ajuste de anchos hoja 2
    # Ajuste de anchos hoja 2
    for i, column_cells in enumerate(ws_baja.columns, start=1):
        col_letter = get_column_letter(i)
        encabezado = ws_baja.cell(row=2, column=i).value
        if encabezado in ['Productos', 'Motivo', 'Observaciones']:
            ws_baja.column_dimensions[col_letter].width = 30
    else:
        # Protege contra columnas sin datos
        try:
            max_length = max(
                (len(str(cell.value)) if cell.value else 0 for cell in column_cells[2:]),
                default=0
            )
        except ValueError:
            max_length = 0
        ws_baja.column_dimensions[col_letter].width = max(15, max_length + 2)

    # --- RESPUESTA HTTP ---
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f'reporte_inventario_y_bajas_{fecha_actual}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    wb.save(response)
    return response

