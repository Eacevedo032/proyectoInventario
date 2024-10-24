import uuid
from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from .models import Categoria
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

# Create your views here.

@login_required
def home(request):
    '''Esto es la pagina principal'''
    categoriasListadas = Categoria.objects.all()
    messages.success(request, '¡Categorias listadas!')  # Mensaje que se mostrará en la plantilla
    return render(request, "gestionCategoria.html", {
        "categorias": categoriasListadas,
        "mensaje": "Hola manos"  # Agregamos el mensaje aquí
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
        return redirect('/')
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

    return redirect('/')

def eliminarCategoria(request, cod_categoria):
    categoria = Categoria.objects.get(cod_categoria = cod_categoria)
    categoria.delete()

    messages.success(request, '¡Categoria eliminada!')

    return redirect('/')