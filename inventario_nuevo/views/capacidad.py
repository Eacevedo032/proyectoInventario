from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Capacidad
from inventario_nuevo.forms import CapacidadForm

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#Gestionar catálogo de la capacidad
@admin_required #Verifica si el usuario es administrador
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