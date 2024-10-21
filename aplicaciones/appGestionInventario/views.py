from django.shortcuts import render, get_object_or_404,redirect
from .models import Categorias
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

# Create your views here.

@login_required
def home(request):
    '''Esto es la pagina principal'''
    categoriasListadas = Categorias.objects.all()
    messages.success(request, '¡Categorias listadas!')  # Mensaje que se mostrará en la plantilla
    return render(request, "gestionCategoria.html", {
        "categorias": categoriasListadas,
        "mensaje": "Hola manos"  # Agregamos el mensaje aquí
    })

def registrarCategoria(request):
    cod_categoria = request.POST['txtCodigo']
    nombre_categoria = request.POST['txtNombre']
    descripcion = request.POST['txtDescripcion']

    categorias = Categorias.objects.create(cod_categoria=cod_categoria, nombre_categoria=nombre_categoria, descripcion=descripcion)
    
    messages.success(request, '¡Categoria registrada!')

    return redirect('/')

@login_required
def edicionCategoria(request, cod_categoria):
    categoria = Categorias.objects.get(cod_categoria = cod_categoria)
    return render(request, "edicionCategoria.html", {"categoria": categoria})

@login_required
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