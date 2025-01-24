from django.shortcuts import render,redirect, get_object_or_404
from .models import Categoria, SubCategoria
from .models import Inventario, DetalleTecnico, DatosComplementarios
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from datetime import datetime
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User #User propio de Django
from django.contrib.auth.decorators import user_passes_test
from .forms import CustomUserCreationForm #Importa el formulario de registro de usuario personalizado de forms.py
from django.utils.safestring import mark_safe #Marca contenido seguro

#Registro de usuario 
def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Desactiva el usuario por defecto
            user.save()
            messages.success(request, mark_safe(
                "Registro exitoso. Tu cuenta será activada tras la aprobación de un administrador. "
            ))
            return render(request, 'registration/register.html', {'form': CustomUserCreationForm()}) #Crea un nuevo formulario vacio cada vez que se desea registrar un nuevo usuario
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def approve_users(request):
    pending_users = User.objects.filter(is_active=False)
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f"Usuario {user.username} aprobado exitosamente.")
        return redirect('approve_users')  # Cambia esta URL según tu configuración

    return render(request, 'admin/approve_users.html', {'pending_users': pending_users})

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
@never_cache
def agregarInventario(request, id_subcategoria):
    subcategoria = get_object_or_404(SubCategoria, id_subcategoria=id_subcategoria)
    categoria = subcategoria.categoria

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        cantidad_disponible = request.POST.get("cantidad_disponible")
        unidad_medida = request.POST.get("unidad_medida", "")
        descripcion = request.POST.get("descripcion", "")
        lote = request.POST.get("lote", "")
        vencimiento = request.POST.get("vencimiento", "").strip()  # Aseguramos que no tenga espacios en blanco
        observaciones = request.POST.get("observaciones", "")

        # Validamos que cantidad_disponible exista y que sea mayor o igual a 0
        if not cantidad_disponible or float(cantidad_disponible) < 0:
            messages.error(request, "La cantidad disponible debe ser un número mayor o igual a 0.")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

        # Validamos campos obligatorios (nombre en este caso)
        if not nombre:
            messages.error(request, "El nombre es un campo obligatorio.")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

        # Validar unicidad del nombre
        if Inventario.objects.filter(nombre=nombre).exists():
            messages.error(request, "El nombre ingresado ya existe en el inventario general, ingrese otro.")
            return render(request, "gestionInventario.html", {"subcategoria": subcategoria})

        # Validar vencimiento (si no está vacío)
        if vencimiento:
            try:
                vencimiento = datetime.strptime(vencimiento, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "El formato de la fecha de vencimiento debe ser YYYY-MM-DD.")
                return render(request, "gestionInventario.html", {"subcategoria": subcategoria})
        else:
            vencimiento = None  # Aseguramos que se guarde como None si está vacío

        try:
            with transaction.atomic():
                inventario = Inventario.objects.create(
                    categoria=categoria,
                    subcategoria=subcategoria,
                    nombre=nombre,
                    cantidad_disponible=float(cantidad_disponible),
                    unidad_medida=unidad_medida,
                    descripcion=descripcion,
                    lote=lote,
                    vencimiento=vencimiento,
                    observaciones=observaciones,
                )
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
                DatosComplementarios.objects.create(
                    inventario=inventario,
                    categoria=categoria,
                    subcategoria=subcategoria,
                    presentacion=request.POST.get("presentacion", ""),
                    accesorios=request.POST.get("accesorios", ""),
                    medidas=request.POST.get("medidas", ""),
                    colores=request.POST.get("colores", ""),
                    capacidad=request.POST.get("capacidad", ""),
                    informacionAdicional=request.POST.get("informacionAdicional", ""),
                )
                messages.success(request, "¡Item agregado correctamente al inventario!")
                return redirect('inventario_general')
        except Exception as e:
            messages.error(request, f"Error al agregar el inventario: {str(e)}")

    return render(request, "gestionInventario.html", {"subcategoria": subcategoria})


#Se uso transaction.atomic() para garantizar que todo el proceso de creación de objetos sea atómico, 
# evitando inconsistencias en caso de error.
#vencimiento.strip(): Se asegura que cualquier valor ingresado para vencimiento no tenga espacios en blanco.
#En Vencimiento: Si el campo está vacío, se guarda como None, Si el formato no es válido, se muestra un mensaje de error claro.

@never_cache #Esto evita que el navegador guarde el estado previo del formulario
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

#Vista solamente para el boton que dice "Ver Inventario General"
@never_cache #Esto evita que el navegador guarde el estado previo del formulario
def verInventarioGeneral(request):
    # Cargar categorías con sus subcategorías e ítems (incluyendo las tablas (clases) relacionadas)
    categorias = Categoria.objects.prefetch_related( #prefetch_related asegura que todos los datos relacionados se carguen de manera eficiente, evitando múltiples consultas innecesarias
        'subcategoria_set__inventario_set__detalle_tecnico',
        'subcategoria_set__inventario_set__datos_complementarios'
    )

    # Pasar las categorías al contexto
    return render(request, "verInventarioGeneral.html", {
        "Categorias": categorias,
    })

@never_cache 
def editarInventario(request, id_inventario):
    # Obtiene el objeto del inventario y sus relaciones
    inventario = get_object_or_404(Inventario, id_inventario=id_inventario)
    detalle_tecnico = get_object_or_404(DetalleTecnico, inventario=inventario)
    datos_complementarios = get_object_or_404(DatosComplementarios, inventario=inventario)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validar y actualizar `nombre tanto si esta vacio como si esta repetido`
                nombre = request.POST.get("nombre", "").strip()
                if not nombre:
                    messages.error(request, "El campo 'Nombre' es obligatorio.")
                    return render(request, "edicionInventario.html", {
                        "subcategoria": inventario.subcategoria,
                        "inventario": inventario,
                        "detalle_tecnico": detalle_tecnico,
                        "datos_complementarios": datos_complementarios,
                    })
                if nombre != inventario.nombre and Inventario.objects.filter(nombre=nombre).exists():
                    messages.error(request, "El nombre ingresado ya existe en el inventario general. Elija otro.")
                    return render(request, "edicionInventario.html", {
                        "subcategoria": inventario.subcategoria,
                        "inventario": inventario,
                        "detalle_tecnico": detalle_tecnico,
                        "datos_complementarios": datos_complementarios,
                    })
                inventario.nombre = nombre

                # Validar y actualizar `cantidad_disponible, campo siempre debe existir y ser igual a 0 o mayor`
                cantidad_disponible = request.POST.get("cantidad_disponible", "").strip()
                if not cantidad_disponible:
                    messages.error(request, "El campo 'Cantidad Disponible' es obligatorio.")
                    return render(request, "edicionInventario.html", {
                        "subcategoria": inventario.subcategoria,
                        "inventario": inventario,
                        "detalle_tecnico": detalle_tecnico,
                        "datos_complementarios": datos_complementarios,
                    })
                try:
                    cantidad_disponible = float(cantidad_disponible)
                    if cantidad_disponible < 0:
                        raise ValueError
                except ValueError:
                    messages.error(request, "La cantidad disponible debe ser un número mayor o igual a 0.")
                    return render(request, "edicionInventario.html", {
                        "subcategoria": inventario.subcategoria,
                        "inventario": inventario,
                        "detalle_tecnico": detalle_tecnico,
                        "datos_complementarios": datos_complementarios,
                    })
                inventario.cantidad_disponible = cantidad_disponible

                # Validar y actualizar `vencimiento que se envie de forma aceptada por el navegador (formato correcto)`
                vencimiento = request.POST.get("vencimiento", "").strip()
                if vencimiento:
                    try:
                        vencimiento = datetime.strptime(vencimiento, "%Y-%m-%d").date()
                    except ValueError:
                        messages.error(request, "El formato de la fecha de vencimiento debe ser YYYY-MM-DD.")
                        return render(request, "edicionInventario.html", {
                            "subcategoria": inventario.subcategoria,
                            "inventario": inventario,
                            "detalle_tecnico": detalle_tecnico,
                            "datos_complementarios": datos_complementarios,
                        })
                else:
                    vencimiento = None
                inventario.vencimiento = vencimiento

                # Actualiza otros campos de Inventario
                inventario.unidad_medida = request.POST.get("unidad_medida", inventario.unidad_medida)
                inventario.descripcion = request.POST.get("descripcion", inventario.descripcion)
                inventario.lote = request.POST.get("lote", inventario.lote)
                inventario.observaciones = request.POST.get("observaciones", inventario.observaciones)
                inventario.save()

                # Actualiza Detalle Técnico y Datos Complementarios
                detalle_tecnico.marca_caracteristica = request.POST.get("marca_caracteristica", detalle_tecnico.marca_caracteristica)
                detalle_tecnico.num_cat = request.POST.get("num_cat", detalle_tecnico.num_cat)
                detalle_tecnico.num_serie = request.POST.get("num_serie", detalle_tecnico.num_serie)
                detalle_tecnico.modelo = request.POST.get("modelo", detalle_tecnico.modelo)
                detalle_tecnico.codigo = request.POST.get("codigo", detalle_tecnico.codigo)
                detalle_tecnico.articulo = request.POST.get("articulo", detalle_tecnico.articulo)
                detalle_tecnico.save()

                datos_complementarios.presentacion = request.POST.get("presentacion", datos_complementarios.presentacion)
                datos_complementarios.accesorios = request.POST.get("accesorios", datos_complementarios.accesorios)
                datos_complementarios.medidas = request.POST.get("medidas", datos_complementarios.medidas)
                datos_complementarios.colores = request.POST.get("colores", datos_complementarios.colores)
                datos_complementarios.capacidad = request.POST.get("capacidad", datos_complementarios.capacidad)
                datos_complementarios.informacionAdicional = request.POST.get("informacionAdicional", datos_complementarios.informacionAdicional)
                datos_complementarios.save()

                messages.success(request, "¡Inventario actualizado exitosamente!")
                return redirect("inventario_general")
        except Exception as e:
            messages.error(request, f"Error al actualizar el inventario: {e}")

    # Pasar cantidad disponible como string formateado
    inventario.cantidad_disponible = f"{inventario.cantidad_disponible:.2f}".replace(',', '.')

    # Renderiza el formulario con los datos cargados
    return render(request, "edicionInventario.html", {
        "subcategoria": inventario.subcategoria,
        "inventario": inventario,
        "detalle_tecnico": detalle_tecnico,
        "datos_complementarios": datos_complementarios,
    })

@never_cache
def eliminarInventario(request, id_inventario):
    try:
        # Obtiene el objeto del inventario
        inventario = get_object_or_404(Inventario, id_inventario=id_inventario)

        # Elimina en cascada (DetalleTecnico y DatosComplementarios)
        inventario.delete()
        messages.success(request, "¡Item eliminado exitosamente!")
    except Exception as e:
        messages.error(request, f"Error al eliminar el item: {e}")

    return redirect("inventario_general")

