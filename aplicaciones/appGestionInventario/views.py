import uuid
from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from .models import Categoria
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
    categoriasListadas = Categoria.objects.all()
  # quite el mensaje de categorias listadas porque aparecia en todas las vistas 
    return render(request, "gestionCategoria.html", {
        "categorias": categoriasListadas,
    })

def registrarCategoria(request):
    if request.method == "POST":
        nombre_categoria = request.POST['txtNombre']
        descripcion = request.POST['txtDescripcion']
        
        # Generar un código de categoría automáticamente (puedes cambiar esto si prefieres otro tipo de generación)
        cod_categoria = str(uuid.uuid4())[:8]  # Aquí se genera un código único de 8 caracteres

        # Crear una nueva categoría, ahora con cod_categoria
        categoria = Categoria.objects.create(
            cod_categoria=cod_categoria,  # El código generado
            nombre_categoria=nombre_categoria,
            descripcion=descripcion
        )

        messages.success(request, '¡Categoría registrada!')
    return redirect('gestionCategoria')
    return render(request, 'registrarCategoria.html')

def edicionCategoria(request, cod_categoria):
    print(f"Buscando categoría con código: {cod_categoria}")
    categorias_existentes = Categoria.objects.values_list('cod_categoria', flat=True)
    print(f"Categorías existentes: {list(categorias_existentes)}")

    try:
        # Intentar obtener la categoría
        categoria = Categoria.objects.get(cod_categoria=cod_categoria)
    except Categoria.DoesNotExist:
        raise Http404("La categoría con este código no existe")

    return render(request, 'edicionCategoria.html', {'categoria': categoria})

@login_required
def editarCategoria(request):
    cod_categoria = request.POST['txtCodigo']
    nombre_categoria = request.POST['txtNombre']
    descripcion = request.POST['txtDescripcion']
    categoria = Categoria.objects.get(cod_categoria = cod_categoria)
    categoria.nombre_categoria = nombre_categoria
    categoria.descripcion = descripcion
    categoria.save()

    messages.success(request, '¡Categoria actualizada!')

    return redirect('gestionCategoria')

def eliminarCategoria(request, cod_categoria):
    categoria = Categoria.objects.get(cod_categoria = cod_categoria)
    categoria.delete()

    messages.success (request, '¡Categoria Eliminada!')

    return redirect('gestionCategoria')