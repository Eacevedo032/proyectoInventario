from django.http import Http404
from django.shortcuts import render,redirect, get_object_or_404
from .models import Categoria, SubCategoria
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.exceptions import ObjectDoesNotExist


# Creación de vistas.

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True) #controla la cache. En otras palabras, siempre 
#deben hacer una nueva solicitud al servidor para obtener la versión más reciente.
def inicio(request):
    '''Esto es la pagina principal'''
     # Mensaje que se mostrará en la plantilla
    return render(request, "inicio.html")

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionCategorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'gestionCategoria.html', {'Categorias': categorias})

def registrarCategoria(request):
    if request.method == "POST":
        nombre_categoria = request.POST['txtNombre']
        descripcion = request.POST['txtDescripcion']

        # Crear la categoría
        categoria = Categoria.objects.create(
            nombre_categoria=nombre_categoria,
            descripcion=descripcion
        )

        messages.success(request, '¡Categoría Registrada!')
        return redirect('gestionCategoria')  # Redirige solo después de la creación

    return render(request, 'registrarCategoria.html')  # Renderiza la plantilla si no es POST

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

def eliminarCategoria(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    categoria.delete()

    messages.success(request, '¡Categoría Eliminada!')

    return redirect('gestionCategoria')

