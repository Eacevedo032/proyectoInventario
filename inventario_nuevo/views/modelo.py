from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Modelo
from inventario_nuevo.forms import ModeloForm

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

# Modelo
@admin_required #Verifica si el usuario es administrador
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
