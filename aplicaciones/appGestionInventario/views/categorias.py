from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from aplicaciones.appGestionInventario.models import Categoria

#Muestra todas las categorías disponibles.
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionCategorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'gestionCategoria.html', {'Categorias': categorias})

#Registra una nueva categoría, verificando si ya existe.
@login_required
def registrarCategoria(request):
    if request.method == "POST":
        nombre_categoria = request.POST['txtNombre'].strip()
        descripcion = request.POST['txtDescripcion']

        # Verificar si la categoría ya existe
        #filter(nombre_categoria=nombre_categoria).exists() comprueba si ya existe uno con ese nombre
        #if not ... exists() crea la categoria si no existe
        if not Categoria.objects.filter(nombre_categoria=nombre_categoria).exists():
            # Crear la categoría si no existe una con el mismo nombre
            Categoria.objects.create(
                nombre_categoria=nombre_categoria,
                descripcion=descripcion
            )
            messages.success(request, '¡Categoría Registrada!')
        else:
            # Mensaje de error si el nombre ya existe
            messages.error(request, 'La categoría ya existe, por favor elige un nombre diferente.')

        return redirect('gestionCategoria')

#Edita una categoría existente.
@login_required
def edicionCategoria(request, id_categoria):
    # Obtener la categoría con el ID proporcionado
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)

    # Verificar si se trata de una solicitud POST para guardar los cambios
    if request.method == "POST":
        nombre_categoria = request.POST['txtNombre']
        descripcion = request.POST.get('txtDescripcion', '')  # Usar .get() para evitar KeyError

        # Asignar un guion si la descripción está vacía
        if not descripcion.strip():  # Comprobar si está vacío o solo espacios
            descripcion = '-'

        categoria.nombre_categoria = nombre_categoria
        categoria.descripcion = descripcion
        categoria.save()

        messages.success(request, '¡Categoría Actualizada!')
        return redirect('gestionCategoria')

    # Si no es POST, muestra el formulario
    return render(request, 'edicionCategoria.html', {'categoria': categoria})

#Elimina una categoría por su ID.
def eliminarCategoria(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    categoria.delete()

    messages.success(request, '¡Categoría Eliminada!')

    return redirect('gestionCategoria')