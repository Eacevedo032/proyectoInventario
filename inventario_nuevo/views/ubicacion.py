from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto, Ubicacion
from inventario_nuevo.forms import UbicacionForm

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