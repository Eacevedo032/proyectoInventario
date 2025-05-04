from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.forms import CategoriaForm, SubcategoriaForm
from inventario_nuevo.models import Categoria, Subcategoria, Producto
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.http import require_GET

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


