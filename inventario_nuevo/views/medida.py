from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto, Medida
from inventario_nuevo.forms import MedidaForm

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@admin_required #Verifica si el usuario es administrador
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