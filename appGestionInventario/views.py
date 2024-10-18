from django.shortcuts import render, get_object_or_404,redirect
from .models import Categorias
from django.contrib import messages

# Create your views here.

def home(request):
    '''Esto es la pagina principal'''
    categoriasListadas = Categorias.objects.all()
    messages.success(request, '¡Categorias listadas!')
    return render(request, "gestionCategoria.html", {"categorias": categoriasListadas})

def registrarCategoria(request):
    cod_categoria = request.POST['txtCodigo']
    nombre_categoria = request.POST['txtNombre']
    descripcion = request.POST['txtDescripcion']

    categorias = Categorias.objects.create(cod_categoria=cod_categoria, nombre_categoria=nombre_categoria, descripcion=descripcion)
    
    messages.success(request, '¡Categoria registrada!')

    return redirect('/')

def edicionCategoria(request, cod_categoria):
    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    
    return render(request, "edicionCategoria.html", {"categoria": categoria})

def editarCategoria(request):
    cod_categoria = request.POST['txtCodigo']
    nombre_categoria = request.POST['txtNombre']
    descripcion = request.POST['txtDescripcion']

    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    categoria.nombre_categoria = nombre_categoria
    categoria.descripcion = descripcion
    categoria.save()

    messages.success(request, '¡Categoria actualizada!')

    return redirect('/')

def eliminarCategoria(request, cod_categoria):
    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    categoria.delete()

    messages.success(request, '¡Categoria eliminada!')

    return redirect('/')