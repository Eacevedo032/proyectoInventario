from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inventario_nuevo.forms import ProductoForm
from inventario_nuevo.models import UnidadMedida
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from decimal import Decimal, InvalidOperation
from inventario_nuevo.forms import CategoriaForm, SubcategoriaForm
from inventario_nuevo.models import Categoria, Subcategoria, Producto, Ubicacion, Lote, Medida
from inventario_nuevo.models import Marca, Modelo, Color, Presentacion, Capacidad, Accesorios, EstadoRecurso, UnidadMedida
from inventario_nuevo.forms import PresentacionForm, CapacidadForm, AccesoriosForm
from inventario_nuevo.forms import MarcaForm, ModeloForm, ColorForm, UbicacionForm, LoteForm, MedidaForm
from django.utils import timezone

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

@admin_required #Verifica si el usuario es administrador
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario_nuevo/listar_productos.html', {'productos': productos})