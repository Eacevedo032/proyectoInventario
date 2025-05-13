from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto, Lote
from inventario_nuevo.forms import LoteForm

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#Vista de Lote
@admin_required #Verifica si el usuario es administrador
def gestionar_lote(request):
    lote_form = LoteForm()
    selected_lote_ids = [int(id) for id in request.GET.getlist('lotes') if id.isdigit()]
    ver_todas = request.GET.get('ver_todas') == '1'

    if ver_todas:
        lotes = Lote.objects.all().order_by('nombre')
    elif selected_lote_ids:
        lotes = Lote.objects.filter(id__in=selected_lote_ids).order_by('nombre')
    else:
        lotes = Lote.objects.none()

    productos = Producto.objects.select_related('lote', 'categoria', 'subcategoria', 'unidad_medida')

    productos_por_lote = {
        lote.id: productos.filter(lote=lote) for lote in lotes
    }

    todos_lotes = Lote.objects.all().order_by('nombre')

    # --- Agregar Lote ---
    if 'guardar_lote' in request.POST:
        lote_form = LoteForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar un lote.")
        elif Lote.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe un lote con ese nombre '{nombre}'.")
        elif lote_form.is_valid():
            lote_form.save()
            messages.success(request, f"Lote '{nombre}' agregado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Lote ---
    elif 'editar_lote' in request.POST:
        lote = get_object_or_404(Lote, id=request.POST.get('lote_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Lote.objects.filter(nombre__iexact=nombre).exclude(id=lote.id).exists():
            messages.warning(request, f"Ya existe un lote con el nombre '{nombre}'.")
        else:
            form = LoteForm(request.POST, instance=lote)
            if form.is_valid():
                form.save()
                messages.success(request, f"Lote '{nombre}' actualizado correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Lote ---
    elif 'eliminar_lote' in request.POST:
        lote = get_object_or_404(Lote, id=request.POST.get('lote_id'))
        if Producto.objects.filter(lote=lote).exists():
            messages.warning(request, f"No se puede eliminar el lote '{lote.nombre}' porque tiene productos asociados.")
        else:
            nombre = lote.nombre
            lote.delete()
            messages.success(request, f"Lote '{nombre}' eliminado correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_lote.html', {
        'lote_form': lote_form,
        'lotes': lotes,
        'productos_por_lote': productos_por_lote,
        'todos_lotes': todos_lotes,
        'lotes_seleccionados': selected_lote_ids,
        'ver_todas': ver_todas,
    })