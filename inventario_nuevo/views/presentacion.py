from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Presentacion
from inventario_nuevo.forms import PresentacionForm

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
