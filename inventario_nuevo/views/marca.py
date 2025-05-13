from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from inventario_nuevo.models import Producto
from inventario_nuevo.models import Marca
from inventario_nuevo.forms import MarcaForm

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

# Marca
@admin_required #Verifica si el usuario es administrador
def gestionar_marca(request):
    marca_form = MarcaForm()

    selected_marcas_ids = request.GET.getlist('marcas')
    mostrar_todas = request.GET.get('ver_todas') == '1'

    if mostrar_todas:
        marcas = Marca.objects.all().order_by('nombre')
    elif selected_marcas_ids:
        marcas = Marca.objects.filter(id__in=selected_marcas_ids).order_by('nombre')
    else:
        marcas = Marca.objects.none()

    productos = Producto.objects.select_related('marca', 'categoria', 'subcategoria', 'unidad_medida')

    #Aquí agrupamos los productos por marca
    productos_por_marca = {}
    for marca in marcas:
        productos_por_marca[marca.id] = productos.filter(marca=marca)

    todas_marcas = Marca.objects.all().order_by('nombre')

    # --- Agregar Marca ---
    if 'guardar_marca' in request.POST:
        marca_form = MarcaForm(request.POST)
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El campo 'Nombre' es obligatorio para agregar una marca.")
        elif Marca.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f"Ya existe una marca con el nombre '{nombre}'.")
        elif marca_form.is_valid():
            marca_form.save()
            messages.success(request, f"Marca '{marca_form.cleaned_data['nombre']}' agregada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Editar Marca ---
    elif 'editar_marca' in request.POST:
        marca = get_object_or_404(Marca, id=request.POST.get('marca_id'))
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.warning(request, "El nombre es obligatorio.")
        elif Marca.objects.filter(nombre__iexact=nombre).exclude(id=marca.id).exists():
            messages.warning(request, f"Ya existe una marca con el nombre '{nombre}'.")
        else:
            form = MarcaForm(request.POST, instance=marca)
            if form.is_valid():
                form.save()
                messages.success(request, f"Marca '{nombre}' actualizada correctamente.")
            return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    # --- Eliminar Marca ---
    elif 'eliminar_marca' in request.POST:
        marca = get_object_or_404(Marca, id=request.POST.get('marca_id'))
        productos_asociados = Producto.objects.filter(marca=marca).exists()

        if productos_asociados:
            messages.warning(request, f"No se puede eliminar la marca '{marca.nombre}' porque tiene productos asociados.")
        else:
            nombre = marca.nombre
            marca.delete()
            messages.success(request, f"Marca '{nombre}' eliminada correctamente.")
        return redirect(request.path + '?' + request.META.get('QUERY_STRING', ''))

    return render(request, 'catalogos/gestionar_marca.html', {
        'marca_form': marca_form,
        'marcas': marcas,
        'productos': productos,
        'productos_por_marca': productos_por_marca, 
        'todas_marcas': todas_marcas,
        'marcas_seleccionadas': [int(id) for id in selected_marcas_ids],
        'ver_todas': mostrar_todas,
    })