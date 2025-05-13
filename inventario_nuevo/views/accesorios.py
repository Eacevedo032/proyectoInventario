from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Accesorios
from inventario_nuevo.forms import AccesoriosForm
from django.views.decorators.http import require_GET

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#Gestionar catálogo de accesorios
@admin_required #Verifica si el usuario es administrador
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