from django.shortcuts import render,redirect, get_object_or_404
from .models import Categoria, SubCategoria
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

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

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionSubcategorias(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    subcategorias = SubCategoria.objects.filter(categoria=categoria)

    return render(request, 'gestionSubcategorias.html', {
        'categoria': categoria,
        'subcategorias': subcategorias
    })

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

def verSubcategorias(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    subcategorias = SubCategoria.objects.filter(categoria=categoria)
    
    return render(request, 'verSubcategorias.html', {
        'categoria': categoria,
        'subcategorias': subcategorias,
    })

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

@login_required
def eliminarSubcategoria(request, id_subcategoria):
    subcategoria = get_object_or_404(SubCategoria, id_subcategoria=id_subcategoria)
    id_categoria = subcategoria.categoria.id_categoria
    subcategoria.delete()

    messages.success(request, '¡Subcategoría Eliminada!')
    return redirect('gestionSubcategorias', id_categoria=id_categoria)
