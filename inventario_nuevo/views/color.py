from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Color
from inventario_nuevo.forms import ColorForm
from django.views.decorators.http import require_GET

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