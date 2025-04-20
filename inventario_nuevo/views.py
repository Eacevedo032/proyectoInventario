from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductoForm
from .models import UnidadMedida
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from decimal import Decimal, InvalidOperation
from .forms import CategoriaForm, SubcategoriaForm
from .models import Categoria, Subcategoria, Producto, Ubicacion, Lote, Medida
from django.http import JsonResponse
from django.db.models import Count, ProtectedError
from django.utils.dateparse import parse_date
from django.db import IntegrityError
from .models import Marca, Modelo, Color, Presentacion, Capacidad, Accesorios, EstadoRecurso, UnidadMedida
from .forms import PresentacionForm, CapacidadForm, AccesoriosForm
from .forms import MarcaForm, ModeloForm, ColorForm, UbicacionForm, LoteForm, MedidaForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from django.utils import timezone

#Vista principal de agregar el producto
@login_required
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
            codigo = request.POST.get('codigo', '').strip()
            if not codigo:
                messages.warning(request, "El código del Lote es obligatorio.")
            elif Lote.objects.filter(codigo__iexact=codigo).exists():
                messages.warning(request, f"Ya existe un Lote con el código '{codigo}'.")
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
            if request.method == 'POST':
                form = ProductoForm(request.POST)

        # Cargar subcategorías válidas antes de validar
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            form.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id)

        if form.is_valid():
            producto = form.save(commit=False)

            # Validación que la cantidad disponible no sea negativa
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

            producto.fecha_agregado = timezone.now()
            producto.save()
            messages.success(request, "Producto agregado correctamente.")
            return redirect('listar_productos')

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

        'hoy': timezone.now().date(),  # Fecha actual en formato date
    })

def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario_nuevo/listar_productos.html', {'productos': productos})

#Vista del menú de los catálogos
@login_required
def menu_catalogos(request):
    return render(request, 'inventario_nuevo/menu_catalogos.html')

# Para los catálogos de Categoría y Subcategoría
def gestionar_catalogos_categoria(request):
    categoria_form = CategoriaForm()
    subcategoria_form = SubcategoriaForm()

    # Filtro de categorías
    selected_categorias_ids = request.GET.getlist('categorias')
    mostrar_todas = request.GET.get('ver_todas') == '1'

    if mostrar_todas:
        categorias = Categoria.objects.all()
    elif selected_categorias_ids:
        categorias = Categoria.objects.filter(id__in=selected_categorias_ids)
    else:
        categorias = Categoria.objects.none()

    categorias = categorias.annotate(
        num_subcategorias=Count('subcategoria', distinct=True)
    ).prefetch_related('subcategoria_set__producto_set')

    subcategorias = Subcategoria.objects.select_related('categoria').prefetch_related('producto_set')
    todas_categorias = Categoria.objects.all()

    # --- Agregar nueva categoría ---
    if 'guardar_categoria' in request.POST:
        categoria_form = CategoriaForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre de la categoría es obligatorio.")
        elif Categoria.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una categoría con el nombre '{nombre}'.")
        elif categoria_form.is_valid():
            categoria_form.save()
            messages.success(request, f"Categoría '{categoria_form.cleaned_data['nombre']}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Agregar nueva subcategoría ---
    elif 'guardar_subcategoria' in request.POST:
        subcategoria_form = SubcategoriaForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre de la subcategoría es obligatorio.")
        elif Subcategoria.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una subcategoría con el nombre '{nombre}'.")
        elif subcategoria_form.is_valid():
            subcategoria_form.save()
            messages.success(request, f"Subcategoría '{subcategoria_form.cleaned_data['nombre']}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar categoría ---
    elif 'editar_categoria' in request.POST:
        categoria = get_object_or_404(Categoria, id=request.POST.get('categoria_id'))
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El nombre de la categoría es obligatorio.")
        elif Categoria.objects.filter(nombre__iexact=nombre).exclude(id=categoria.id).exists():
            messages.warning(request, f"Ya existe una categoría con el nombre '{nombre}'.")
        else:
            form = CategoriaForm(request.POST, instance=categoria)
            if form.is_valid():
                form.save()
                messages.success(request, f"La categoría '{nombre}' fue actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar subcategoría ---
    elif 'editar_subcategoria' in request.POST:
        sub = get_object_or_404(Subcategoria, id=request.POST.get('subcategoria_id'))
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El nombre de la subcategoría es obligatorio.")
        elif Subcategoria.objects.filter(nombre__iexact=nombre).exclude(id=sub.id).exists():
            messages.warning(request, f"Ya existe una subcategoría con el nombre '{nombre}'.")
        else:
            sub.nombre = nombre
            sub.descripcion = request.POST.get('descripcion', '').strip()
            sub.save()
            messages.success(request, f'Subcategoría "{nombre}" actualizada correctamente.')
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar categoría ---
    elif 'eliminar_categoria' in request.POST:
        categoria = get_object_or_404(Categoria, id=request.POST.get('categoria_id'))
        subcategorias = Subcategoria.objects.filter(categoria=categoria)
        productos = Producto.objects.filter(subcategoria__categoria=categoria).distinct()

        if subcategorias.exists() or productos.exists():
            messages.warning(request, f"No se puede eliminar la categoría '{categoria.nombre}' porque posee subcategorías asociadas.")
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f"La categoría '{nombre}' fue eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar subcategoría ---
    elif 'eliminar_subcategoria' in request.POST:
        sub = get_object_or_404(Subcategoria, id=request.POST.get('subcategoria_id'))
        if sub.producto_set.exists():
            messages.warning(request, f'No se puede eliminar la subcategoría "{sub.nombre}" porque posee productos asociados.')
        else:
            nombre = sub.nombre
            sub.delete()
            messages.success(request, f'Subcategoría "{nombre}" eliminada correctamente.')
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'inventario_nuevo/catalogos_categoria.html', {
        'categoria_form': categoria_form,
        'subcategoria_form': subcategoria_form,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'todas_categorias': todas_categorias,
        'categorias_seleccionadas': [int(id) for id in selected_categorias_ids],
        'ver_todas': mostrar_todas,
    })
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Subcategoria

@require_GET
def obtener_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    
    try:
        categoria_id = int(categoria_id)
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)

    try:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id
        ).order_by('nombre').values('id', 'nombre')

        return JsonResponse(list(subcategorias), safe=False)
    except Exception as e:
        print(f"Error en obtener_subcategorias: {str(e)}")
        return JsonResponse([], safe=False)

#Menu principal de Inicio del Inventario.
@login_required
def menu_inventario(request):
    return render(request, 'inventario_nuevo/menu_inventario.html')

# Marca
def gestionar_marca(request):
    marca_form = MarcaForm()

    selected_marcas_ids = request.GET.getlist('marcas')
    mostrar_todas = request.GET.get('ver_todas') == '1'

    if mostrar_todas:
        marcas = Marca.objects.all().order_by('nombre')
    elif selected_marcas_ids:
        marcas = Marca.objects.filter(id__in=selected_marcas_ids).order_by('nombre')
    else:
        marcas = Marca.objects.none()

    productos = Producto.objects.select_related('marca', 'categoria', 'subcategoria', 'unidad_medida')

    #Aquí agrupamos los productos por marca
    productos_por_marca = {}
    for marca in marcas:
        productos_por_marca[marca.id] = productos.filter(marca=marca)

    todas_marcas = Marca.objects.all().order_by('nombre')

    # --- Agregar Marca ---
    if 'guardar_marca' in request.POST:
        marca_form = MarcaForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar una marca.")
        elif Marca.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una marca con el nombre '{nombre}'.")
        elif marca_form.is_valid():
            marca_form.save()
            messages.success(request, f"Marca '{marca_form.cleaned_data['nombre']}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Marca ---
    elif 'editar_marca' in request.POST:
        marca = get_object_or_404(Marca, id=request.POST.get('marca_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Marca.objects.filter(nombre__iexact=nombre).exclude(id=marca.id).exists():
            messages.warning(request, f"Ya existe una marca con el nombre '{nombre}'.")
        else:
            form = MarcaForm(request.POST, instance=marca)
            if form.is_valid():
                form.save()
                messages.success(request, f"Marca '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Marca ---
    elif 'eliminar_marca' in request.POST:
        marca = get_object_or_404(Marca, id=request.POST.get('marca_id'))
        productos_asociados = Producto.objects.filter(marca=marca).exists()

        if productos_asociados:
            messages.warning(request, f"No se puede eliminar la marca '{marca.nombre}' porque tiene productos asociados.")
        else:
            nombre = marca.nombre
            marca.delete()
            messages.success(request, f"Marca '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_marca.html', {
        'marca_form': marca_form,
        'marcas': marcas,
        'productos': productos,
        'productos_por_marca': productos_por_marca, 
        'todas_marcas': todas_marcas,
        'marcas_seleccionadas': [int(id) for id in selected_marcas_ids],
        'ver_todas': mostrar_todas,
    })

# Modelo
def gestionar_modelo(request):
    modelo_form = ModeloForm()

    selected_modelos_ids = [int(id) for id in request.GET.getlist('modelos') if id.isdigit()]
    mostrar_todas = request.GET.get('ver_todos') == '1'

    if mostrar_todas:
        modelos = Modelo.objects.all().order_by('nombre')
    elif selected_modelos_ids:
        modelos = Modelo.objects.filter(id__in=selected_modelos_ids).order_by('nombre')
    else:
        modelos = Modelo.objects.none()

    productos = Producto.objects.select_related('modelo', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_modelo = {}
    for modelo in modelos:
        productos_por_modelo[modelo.id] = productos.filter(modelo=modelo)

    todos_modelos = Modelo.objects.all().order_by('nombre')

    # --- Agregar Modelo ---
    if 'guardar_modelo' in request.POST:
        modelo_form = ModeloForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar un modelo.")
        elif Modelo.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe un modelo con el nombre '{nombre}'.")
        elif modelo_form.is_valid():
            modelo_form.save()
            messages.success(request, f"Modelo '{modelo_form.cleaned_data['nombre']}' agregado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Modelo ---
    elif 'editar_modelo' in request.POST:
        modelo = get_object_or_404(Modelo, id=request.POST.get('modelo_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Modelo.objects.filter(nombre__iexact=nombre).exclude(id=modelo.id).exists():
            messages.warning(request, f"Ya existe un modelo con el nombre '{nombre}'.")
        else:
            form = ModeloForm(request.POST, instance=modelo)
            if form.is_valid():
                form.save()
                messages.success(request, f"Modelo '{nombre}' actualizado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Modelo ---
    elif 'eliminar_modelo' in request.POST:
        modelo = get_object_or_404(Modelo, id=request.POST.get('modelo_id'))
        productos_asociados = Producto.objects.filter(modelo=modelo).exists()

        if productos_asociados:
            messages.warning(request, f"No se puede eliminar el modelo '{modelo.nombre}' porque tiene productos asociados.")
        else:
            nombre = modelo.nombre
            modelo.delete()
            messages.success(request, f"Modelo '{nombre}' eliminado correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_modelo.html', {
        'modelo_form': modelo_form,
        'modelos': modelos,
        'productos': productos,
        'productos_por_modelo': productos_por_modelo,
        'todos_modelos': todos_modelos,
        'modelos_seleccionados': selected_modelos_ids,
        'ver_todas': mostrar_todas,
    })

# Color
def gestionar_color(request):
    color_form = ColorForm()

    selected_colores_ids = [int(id) for id in request.GET.getlist('colores') if id.isdigit()]
    mostrar_todos = request.GET.get('ver_todos') == '1'

    if mostrar_todos:
        colores = Color.objects.all().order_by('nombre')
    elif selected_colores_ids:
        colores = Color.objects.filter(id__in=selected_colores_ids).order_by('nombre')
    else:
        colores = Color.objects.none()

    productos = Producto.objects.select_related('color', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_color = {}
    for color in colores:
        productos_por_color[color.id] = productos.filter(color=color)

    todos_colores = Color.objects.all().order_by('nombre')

    # --- Agregar Color ---
    if 'guardar_color' in request.POST:
        color_form = ColorForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar un color.")
        elif Color.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe un color con el nombre '{nombre}'.")
        elif color_form.is_valid():
            color_form.save()
            messages.success(request, f"Color '{color_form.cleaned_data['nombre']}' agregado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Color ---
    elif 'editar_color' in request.POST:
        color = get_object_or_404(Color, id=request.POST.get('color_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Color.objects.filter(nombre__iexact=nombre).exclude(id=color.id).exists():
            messages.warning(request, f"Ya existe un color con el nombre '{nombre}'.")
        else:
            form = ColorForm(request.POST, instance=color)
            if form.is_valid():
                form.save()
                messages.success(request, f"Color '{nombre}' actualizado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Color ---
    elif 'eliminar_color' in request.POST:
        color = get_object_or_404(Color, id=request.POST.get('color_id'))
        productos_asociados = Producto.objects.filter(color=color).exists()

        if productos_asociados:
            messages.warning(request, f"No se puede eliminar el color '{color.nombre}' porque tiene productos asociados.")
        else:
            nombre = color.nombre
            color.delete()
            messages.success(request, f"Color '{nombre}' eliminado correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_color.html', {
        'color_form': color_form,
        'colores': colores,
        'productos': productos,
        'productos_por_color': productos_por_color,
        'todos_colores': todos_colores,
        'colores_seleccionados': selected_colores_ids,
        'ver_todas': mostrar_todos,
    })

#Gestionar el catálogo de Presentación
def gestionar_presentacion(request):
    presentacion_form = PresentacionForm()

    selected_ids = [int(id) for id in request.GET.getlist('presentaciones') if id.isdigit()]
    mostrar_todos = request.GET.get('ver_todos') == '1'

    if mostrar_todos:
        presentaciones = Presentacion.objects.all().order_by('nombre')
    elif selected_ids:
        presentaciones = Presentacion.objects.filter(id__in=selected_ids).order_by('nombre')
    else:
        presentaciones = Presentacion.objects.none()

    productos = Producto.objects.select_related('presentacion', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_presentacion = {}
    for pres in presentaciones:
        productos_por_presentacion[pres.id] = productos.filter(presentacion=pres)

    todos = Presentacion.objects.all().order_by('nombre')

    if 'guardar_presentacion' in request.POST:
        presentacion_form = PresentacionForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio.")
        elif Presentacion.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una presentación con el nombre '{nombre}'.")
        elif presentacion_form.is_valid():
            presentacion_form.save()
            messages.success(request, f"Presentación '{nombre}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'editar_presentacion' in request.POST:
        presentacion = get_object_or_404(Presentacion, id=request.POST.get('presentacion_id'))
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Presentacion.objects.filter(nombre__iexact=nombre).exclude(id=presentacion.id).exists():
            messages.warning(request, f"Ya existe una presentación con el nombre '{nombre}'.")
        else:
            form = PresentacionForm(request.POST, instance=presentacion)
            if form.is_valid():
                form.save()
                messages.success(request, f"Presentación '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'eliminar_presentacion' in request.POST:
        presentacion = get_object_or_404(Presentacion, id=request.POST.get('presentacion_id'))
        if Producto.objects.filter(presentacion=presentacion).exists():
            messages.warning(request, f"No se puede eliminar la presentación '{presentacion.nombre}' porque tiene productos asociados.")
        else:
            nombre = presentacion.nombre
            presentacion.delete()
            messages.success(request, f"Presentación '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_presentacion.html', {
        'presentacion_form': presentacion_form,
        'presentaciones': presentaciones,
        'productos_por_presentacion': productos_por_presentacion,
        'todas_presentaciones': todos,
        'presentaciones_seleccionadas': selected_ids,
        'ver_todas': mostrar_todos,
    })

#Gestionar catálogo de la capacidad
def gestionar_capacidad(request):
    capacidad_form = CapacidadForm()

    selected_ids = [int(id) for id in request.GET.getlist('capacidades') if id.isdigit()]
    mostrar_todos = request.GET.get('ver_todos') == '1'

    if mostrar_todos:
        capacidades = Capacidad.objects.all().order_by('nombre')
    elif selected_ids:
        capacidades = Capacidad.objects.filter(id__in=selected_ids).order_by('nombre')
    else:
        capacidades = Capacidad.objects.none()

    productos = Producto.objects.select_related('capacidad', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_capacidad = {}
    for cap in capacidades:
        productos_por_capacidad[cap.id] = productos.filter(capacidad=cap)

    todos = Capacidad.objects.all().order_by('nombre')

    if 'guardar_capacidad' in request.POST:
        capacidad_form = CapacidadForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio.")
        elif Capacidad.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una capacidad con el nombre '{nombre}'.")
        elif capacidad_form.is_valid():
            capacidad_form.save()
            messages.success(request, f"Capacidad '{nombre}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'editar_capacidad' in request.POST:
        capacidad = get_object_or_404(Capacidad, id=request.POST.get('capacidad_id'))
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Capacidad.objects.filter(nombre__iexact=nombre).exclude(id=capacidad.id).exists():
            messages.warning(request, f"Ya existe una capacidad con el nombre '{nombre}'.")
        else:
            form = CapacidadForm(request.POST, instance=capacidad)
            if form.is_valid():
                form.save()
                messages.success(request, f"Capacidad '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'eliminar_capacidad' in request.POST:
        capacidad = get_object_or_404(Capacidad, id=request.POST.get('capacidad_id'))
        if Producto.objects.filter(capacidad=capacidad).exists():
            messages.warning(request, f"No se puede eliminar la capacidad '{capacidad.nombre}' porque tiene productos asociados.")
        else:
            nombre = capacidad.nombre
            capacidad.delete()
            messages.success(request, f"Capacidad '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_capacidad.html', {
        'capacidad_form': capacidad_form,
        'capacidades': capacidades,
        'productos_por_capacidad': productos_por_capacidad,
        'todas_capacidades': todos,
        'capacidades_seleccionadas': selected_ids,
        'ver_todas': mostrar_todos,
    })

#Gestionar catálogo de accesorios
def gestionar_accesorios(request):
    accesorios_form = AccesoriosForm()

    selected_ids = [int(id) for id in request.GET.getlist('accesorios') if id.isdigit()]
    mostrar_todos = request.GET.get('ver_todos') == '1'

    if mostrar_todos:
        accesorios = Accesorios.objects.all().order_by('nombre')
    elif selected_ids:
        accesorios = Accesorios.objects.filter(id__in=selected_ids).order_by('nombre')
    else:
        accesorios = Accesorios.objects.none()

    productos = Producto.objects.select_related('accesorios', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_accesorio = {}
    for acc in accesorios:
        productos_por_accesorio[acc.id] = productos.filter(accesorios=acc)

    todos = Accesorios.objects.all().order_by('nombre')

    if 'guardar_accesorios' in request.POST:
        accesorios_form = AccesoriosForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio.")
        elif Accesorios.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe un accesorio con el nombre '{nombre}'.")
        elif accesorios_form.is_valid():
            accesorios_form.save()
            messages.success(request, f"Accesorio '{nombre}' agregado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'editar_accesorios' in request.POST:
        accesorio = get_object_or_404(Accesorios, id=request.POST.get('accesorios_id'))
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Accesorios.objects.filter(nombre__iexact=nombre).exclude(id=accesorio.id).exists():
            messages.warning(request, f"Ya existe un accesorio con el nombre '{nombre}'.")
        else:
            form = AccesoriosForm(request.POST, instance=accesorio)
            if form.is_valid():
                form.save()
                messages.success(request, f"Accesorio '{nombre}' actualizado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    elif 'eliminar_accesorios' in request.POST:
        accesorio = get_object_or_404(Accesorios, id=request.POST.get('accesorios_id'))
        if Producto.objects.filter(accesorios=accesorio).exists():
            messages.warning(request, f"No se puede eliminar el accesorio '{accesorio.nombre}' porque tiene productos asociados.")
        else:
            nombre = accesorio.nombre
            accesorio.delete()
            messages.success(request, f"Accesorio '{nombre}' eliminado correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_accesorios.html', {
        'accesorios_form': accesorios_form,
        'accesorios': accesorios,
        'productos_por_accesorio': productos_por_accesorio,
        'todos_accesorios': todos,
        'accesorios_seleccionados': selected_ids,
        'ver_todas': mostrar_todos,
    })

#Gestionar Ubicación del Producto
def gestionar_ubicacion(request):
    ubicacion_form = UbicacionForm()
    selected_ubicaciones_ids = [int(id) for id in request.GET.getlist('ubicaciones') if id.isdigit()]

    ver_todas = request.GET.get('ver_todas') == '1'

    if ver_todas:
        ubicaciones = Ubicacion.objects.all().order_by('nombre')
    elif selected_ubicaciones_ids:
        ubicaciones = Ubicacion.objects.filter(id__in=selected_ubicaciones_ids).order_by('nombre')
    else:
        ubicaciones = Ubicacion.objects.none()

    productos = Producto.objects.select_related('ubicacion', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_ubicacion = {
        ubicacion.id: productos.filter(ubicacion=ubicacion) for ubicacion in ubicaciones
    }

    todas_ubicaciones = Ubicacion.objects.all().order_by('nombre')

    # --- Agregar Ubicación ---
    if 'guardar_ubicacion' in request.POST:
        ubicacion_form = UbicacionForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar una ubicación.")
        elif Ubicacion.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una ubicación con el nombre '{nombre}'.")
        elif ubicacion_form.is_valid():
            ubicacion_form.save()
            messages.success(request, f"Ubicación '{ubicacion_form.cleaned_data['nombre']}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Ubicación ---
    elif 'editar_ubicacion' in request.POST:
        ubicacion = get_object_or_404(Ubicacion, id=request.POST.get('ubicacion_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Ubicacion.objects.filter(nombre__iexact=nombre).exclude(id=ubicacion.id).exists():
            messages.warning(request, f"Ya existe una ubicación con el nombre '{nombre}'.")
        else:
            form = UbicacionForm(request.POST, instance=ubicacion)
            if form.is_valid():
                form.save()
                messages.success(request, f"Ubicación '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Ubicación ---
    elif 'eliminar_ubicacion' in request.POST:
        ubicacion = get_object_or_404(Ubicacion, id=request.POST.get('ubicacion_id'))
        productos_asociados = Producto.objects.filter(ubicacion=ubicacion).exists()

        if productos_asociados:
            messages.warning(request, f"No se puede eliminar la ubicación '{ubicacion.nombre}' porque tiene productos asociados.")
        else:
            nombre = ubicacion.nombre
            ubicacion.delete()
            messages.success(request, f"Ubicación '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_ubicacion.html', {
        'ubicacion_form': ubicacion_form,
        'ubicaciones': ubicaciones,
        'productos': productos,
        'productos_por_ubicacion': productos_por_ubicacion,
        'todas_ubicaciones': todas_ubicaciones,
        'ubicaciones_seleccionadas': selected_ubicaciones_ids,
        'ver_todas': ver_todas,  
    })

#Vista de Lote
def gestionar_lote(request):
    lote_form = LoteForm()
    selected_lote_ids = [int(id) for id in request.GET.getlist('lotes') if id.isdigit()]
    ver_todas = request.GET.get('ver_todas') == '1'

    if ver_todas:
        lotes = Lote.objects.all().order_by('codigo')
    elif selected_lote_ids:
        lotes = Lote.objects.filter(id__in=selected_lote_ids).order_by('codigo')
    else:
        lotes = Lote.objects.none()

    productos = Producto.objects.select_related('lote', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_lote = {
        lote.id: productos.filter(lote=lote) for lote in lotes
    }

    todos_lotes = Lote.objects.all().order_by('codigo')

    # --- Agregar Lote ---
    if 'guardar_lote' in request.POST:
        lote_form = LoteForm(request.POST)
        codigo = request.POST.get('codigo', '').strip()

        if not codigo:
            messages.warning(request, "El campo 'Código' es obligatorio para agregar un lote.")
        elif Lote.objects.filter(codigo__iexact=codigo).exists():
            messages.warning(request, f"Ya existe un lote con el código '{codigo}'.")
        elif lote_form.is_valid():
            lote_form.save()
            messages.success(request, f"Lote '{codigo}' agregado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Lote ---
    elif 'editar_lote' in request.POST:
        lote = get_object_or_404(Lote, id=request.POST.get('lote_id'))
        codigo = request.POST.get('codigo', '').strip()

        if not codigo:
            messages.warning(request, "El código es obligatorio.")
        elif Lote.objects.filter(codigo__iexact=codigo).exclude(id=lote.id).exists():
            messages.warning(request, f"Ya existe un lote con el código '{codigo}'.")
        else:
            form = LoteForm(request.POST, instance=lote)
            if form.is_valid():
                form.save()
                messages.success(request, f"Lote '{codigo}' actualizado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Lote ---
    elif 'eliminar_lote' in request.POST:
        lote = get_object_or_404(Lote, id=request.POST.get('lote_id'))
        if Producto.objects.filter(lote=lote).exists():
            messages.warning(request, f"No se puede eliminar el lote '{lote.codigo}' porque tiene productos asociados.")
        else:
            codigo = lote.codigo
            lote.delete()
            messages.success(request, f"Lote '{codigo}' eliminado correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_lote.html', {
        'lote_form': lote_form,
        'lotes': lotes,
        'productos_por_lote': productos_por_lote,
        'todos_lotes': todos_lotes,
        'lotes_seleccionados': selected_lote_ids,
        'ver_todas': ver_todas,
    })

#Vista de Medida del Producto
def gestionar_medida(request):
    medida_form = MedidaForm()
    selected_medidas_ids = [int(id) for id in request.GET.getlist('medidas') if id.isdigit()]
    ver_todas = request.GET.get('ver_todas') == '1'

    if ver_todas:
        medidas = Medida.objects.all().order_by('nombre')
    elif selected_medidas_ids:
        medidas = Medida.objects.filter(id__in=selected_medidas_ids).order_by('nombre')
    else:
        medidas = Medida.objects.none()

    productos = Producto.objects.select_related('medida', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_medida = {
        medida.id: productos.filter(medida=medida) for medida in medidas
    }

    todas_medidas = Medida.objects.all().order_by('nombre')

    # --- Agregar Medida ---
    if 'guardar_medida' in request.POST:
        medida_form = MedidaForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar una medida.")
        elif Medida.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una medida con el nombre '{nombre}'.")
        elif medida_form.is_valid():
            medida_form.save()
            messages.success(request, f"Medida '{nombre}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Medida ---
    elif 'editar_medida' in request.POST:
        medida = get_object_or_404(Medida, id=request.POST.get('medida_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Medida.objects.filter(nombre__iexact=nombre).exclude(id=medida.id).exists():
            messages.warning(request, f"Ya existe una medida con el nombre '{nombre}'.")
        else:
            form = MedidaForm(request.POST, instance=medida)
            if form.is_valid():
                form.save()
                messages.success(request, f"Medida '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Medida ---
    elif 'eliminar_medida' in request.POST:
        medida = get_object_or_404(Medida, id=request.POST.get('medida_id'))
        if Producto.objects.filter(medida=medida).exists():
            messages.warning(request, f"No se puede eliminar la medida '{medida.nombre}' porque tiene productos asociados.")
        else:
            nombre = medida.nombre
            medida.delete()
            messages.success(request, f"Medida '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_medida.html', {
        'medida_form': medida_form,
        'medidas': medidas,
        'productos_por_medida': productos_por_medida,
        'todas_medidas': todas_medidas,
        'medidas_seleccionadas': selected_medidas_ids,
        'ver_todas': ver_todas,
    })

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
