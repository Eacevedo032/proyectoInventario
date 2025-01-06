from django.shortcuts import render,redirect, get_object_or_404
from .models import Categoria, SubCategoria
from .models import Inventario, DetalleTecnico, DatosComplementarios
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
#from django.db import IntegrityError
from datetime import datetime
from django.db import transaction

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

#.strip() se utiliza para evitar que los espacios en blanco adicionales causen errores 
# o inconsistencias en la base de datos.

# Aquí empieza la vista del Inventario

@login_required
def agregarInventario(request, id_subcategoria):
    # Obtener la subcategoría y su categoría
    subcategoria = get_object_or_404(SubCategoria, id_subcategoria=id_subcategoria)
    categoria = subcategoria.categoria

    if request.method == "POST":
        # Obtener campos del formulario
        nombre = request.POST.get("nombre")
        cantidad_disponible = request.POST.get("cantidad_disponible", None)
        descripcion = request.POST.get("descripcion", "") # ()"") se guardan como cadenas vacias en la BD (ideal para campos que aplican pero no hay datos) 
        lote = request.POST.get("lote", "")
        vencimiento = request.POST.get("vencimiento", None) # Django traduce este valor a NULL en la base de datos. Ideal para campos que no aplican necesariamente
        observaciones = request.POST.get("observaciones", "")

        # Validar campos obligatorios
        if not nombre or not cantidad_disponible:
            messages.error(request, "El nombre y la cantidad disponible son campos obligatorios.")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

        # Validar unicidad del nombre
        if Inventario.objects.filter(nombre=nombre).exists():
            messages.error(request, "El nombre ingresado ya existe en el inventario general, ingrese otro.")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

        # Validar y procesar el campo de vencimiento
        if vencimiento:
            try:
                # Intentar convertir el formato de fecha recibido
                vencimiento = datetime.strptime(vencimiento, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "El formato de la fecha de vencimiento debe ser YYYY-MM-DD.")
                return render(request, "gestionInventario.html", {"subcategoria": subcategoria})
        else:
            # Si no se proporciona una fecha de vencimiento, establecer como None
            vencimiento = None

        # Transacción para asegurarnos de que todo o nada se guarde
        try:
            with transaction.atomic():
                # Crear el objeto Inventario
                inventario = Inventario.objects.create(
                    categoria=categoria,
                    subcategoria=subcategoria,
                    nombre=nombre,
                    cantidad_disponible=cantidad_disponible,
                    descripcion=descripcion,
                    lote=lote,
                    vencimiento=vencimiento,
                    observaciones=observaciones,
                )

                # Crear el objeto Detalle Técnico
                DetalleTecnico.objects.create(
                    inventario=inventario,
                    categoria=categoria,
                    subcategoria=subcategoria,
                    marca_caracteristica=request.POST.get("marca_caracteristica", ""),
                    num_cat=request.POST.get("num_cat", ""),
                    num_serie=request.POST.get("num_serie", ""),
                    modelo=request.POST.get("modelo", ""),
                    codigo=request.POST.get("codigo", ""),
                    articulo=request.POST.get("articulo", ""),
                )

                # Crear el objeto Datos Complementarios
                DatosComplementarios.objects.create(
                    inventario=inventario,  # Asociar al inventario creado
                    categoria=categoria, # Asocia a la Categoria
                    subcategoria=subcategoria, #Asocia a la Subcategoria
                    presentacion=request.POST.get("presentacion", ""),
                    accesorios=request.POST.get("accesorios", ""),
                    medidas=request.POST.get("medidas", ""),
                    colores=request.POST.get("colores", ""),
                    capacidad=request.POST.get("capacidad", ""),
                    informacionAdicional=request.POST.get("informacionAdicional", ""),
                )

            # Mensaje de éxito
            messages.success(request, "¡Item agregado correctamente al inventario!")
            return redirect('inventario_general') #Me dirige a la vista de Inventario General si es exitosa

        except Exception as e:
            # Capturar cualquier error y enviar un mensaje
            messages.error(request, f"Error al agregar el inventario: {str(e)}")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

    # Si el método no es POST, renderizar el formulario vacío
    return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

#Se uso transaction.atomic() para garantizar que todo el proceso de creación de objetos sea atómico, 
# evitando inconsistencias en caso de error.


# Vista del Inventario General
def inventario_general(request):
    # Cargar categorías con sus subcategorías e ítems (incluyendo las tablas (clases) relacionadas)
    categorias = Categoria.objects.prefetch_related( #prefetch_related asegura que todos los datos relacionados se carguen de manera eficiente, evitando múltiples consultas innecesarias
        'subcategoria_set__inventario_set__detalle_tecnico',
        'subcategoria_set__inventario_set__datos_complementarios'
    )

    # Pasar las categorías al contexto
    return render(request, "inventarioGeneral.html", {
        "Categorias": categorias,
    })