from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from aplicaciones.appGestionInventario.models import Categoria, SubCategoria

#Gestiona las subcategorías de una categoría específica.
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionSubcategorias(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    subcategorias = SubCategoria.objects.filter(categoria=categoria)

    return render(request, 'gestionSubcategorias.html', {
        'categoria': categoria,
        'subcategorias': subcategorias
    })

#Agrega una nueva subcategoría a una categoría específica.
@login_required
def agregarSubcategoria(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)

    if request.method == "POST":
        nombre = request.POST['txtNombreSubcategoria'].strip()

        # Verificar si la subcategoría ya existe
        if not SubCategoria.objects.filter(nombre=nombre, categoria=categoria).exists():
            SubCategoria.objects.create(nombre=nombre, categoria=categoria)
            messages.success(request, '¡Subcategoría Registrada!')
        else:
            messages.error(request, 'La subcategoría ya existe, ingrese otra.')

    return redirect('gestionSubcategorias', id_categoria=id_categoria)

#Edita una subcategoría existente.
@login_required
def editarSubcategoria(request, id_subcategoria):
    # Obtener la subcategoría con el ID proporcionado
    subcategoria = get_object_or_404(SubCategoria, id_subcategoria=id_subcategoria)

    if request.method == "POST":
        nombre = request.POST.get('txtNombre', '').strip()
        if nombre:
            subcategoria.nombre = nombre
            subcategoria.save()
            messages.success(request, '¡Subcategoría Actualizada!')
            # Redirige a la vista de gestión de subcategorías de la categoría
            return redirect('gestionSubcategorias', id_categoria=subcategoria.categoria.id_categoria)
        else:
            messages.error(request, 'El nombre no puede estar vacío.')

    # Renderiza la plantilla de edición si no es POST
    return render(request, 'edicionSubcategoria.html', {'subcategoria': subcategoria})

#Elimina una subcategoría específica.
@login_required
def eliminarSubcategoria(request, id_subcategoria):
    subcategoria = get_object_or_404(SubCategoria, id_subcategoria=id_subcategoria)
    id_categoria = subcategoria.categoria.id_categoria
    subcategoria.delete()

    messages.success(request, '¡Subcategoría Eliminada!')
    return redirect('gestionSubcategorias', id_categoria=id_categoria)

#.strip() se utiliza para evitar que los espacios en blanco adicionales causen errores 
# o inconsistencias en la base de datos.