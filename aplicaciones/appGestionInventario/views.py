from django.shortcuts import render, get_object_or_404,redirect
from .models import Categorias
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
    categoriasListadas = Categorias.objects.all()
  # quite el mensaje de categorias listadas porque aparecia en todas las vistas 
    return render(request, "gestionCategoria.html", {
        "categorias": categoriasListadas,
    })

def registrarCategoria(request):
    cod_categoria = request.POST['txtCodigo']
    nombre_categoria = request.POST['txtNombre']
    descripcion = request.POST['txtDescripcion']
    categorias = Categorias.objects.create(cod_categoria=cod_categoria, nombre_categoria=nombre_categoria, descripcion=descripcion)
    messages.success(request, '¡Categoria registrada!')
    return redirect('gestionCategoria')

@login_required
def edicionCategoria(request, cod_categoria):
    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    return render(request, "edicionCategoria.html", {"categoria": categoria})

@login_required
def editarCategoria(request):
    try:
        cod_categoria = request.POST['txtCodigo']
        nombre_categoria = request.POST['txtNombre']
        descripcion = request.POST['txtDescripcion']
        
        # Buscar la categoría existente en la base de datos
        categoria = Categorias.objects.get(cod_categoria=cod_categoria)
        
        # Actualizar los campos de la categoría
        categoria.nombre_categoria = nombre_categoria
        categoria.descripcion = descripcion
        categoria.save()

        # Mensaje de éxito
        messages.success(request, '¡Categoria actualizada!')

        # Redirigir a la vista 'gestionCategoria'
        return redirect('gestionCategoria')
    except ObjectDoesNotExist:
        messages.error(request, 'La categoría no existe.')
        return redirect('gestionCategoria')

def eliminarCategoria(request, cod_categoria):
    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    categoria.delete()

    messages.success (request, '¡Categoria Eliminada!')

    return redirect('gestionCategoria')