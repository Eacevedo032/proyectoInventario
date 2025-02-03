from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from datetime import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required,  user_passes_test
from aplicaciones.appGestionInventario.models import Categoria, SubCategoria, Inventario, DetalleTecnico, DatosComplementarios, GuardadoInventarioGeneral
from django.utils.timezone import localtime
from django.utils.timezone import now

'''agregarInventario

Permite agregar un nuevo ítem al inventario de una subcategoría específica.
Valida que los campos obligatorios (como nombre y cantidad_disponible) estén completos y sean correctos.
Verifica que el nombre no esté repetido en el inventario general.
Asegura que la cantidad disponible sea un número mayor o igual a 0.
Valida el formato de la fecha de vencimiento (si se proporciona).
Usa transaction.atomic() para garantizar que la creación de objetos sea atómica y evitar inconsistencias.
Si todo es válido, crea un objeto de inventario junto con sus relaciones (DetalleTecnico y DatosComplementarios).'''
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
# evitando inconsistencias en caso de error (si algo falla, se revierte todo).
#vencimiento.strip(): Se asegura que cualquier valor ingresado para vencimiento no tenga espacios en blanco.
#En Vencimiento: Si el campo está vacío, se guarda como None, Si el formato no es válido, se muestra un mensaje de error claro.

'''inventario_general

Carga todas las categorías, junto con sus subcategorías y los ítems relacionados (incluyendo las tablas relacionadas DetalleTecnico y DatosComplementarios).
Usa prefetch_related para optimizar las consultas a la base de datos y evitar múltiples consultas innecesarias.
Devuelve un contexto que incluye las categorías y subcategorías con sus ítems.'''
@never_cache #Esto evita que el navegador guarde el estado previo del formulario
def inventario_general(request):
    # Cargar categorías con sus subcategorías e ítems (incluyendo las relaciones OneToOne)
    categorias = Categoria.objects.prefetch_related(
        'subcategoria_set__inventario_set__detalle_tecnico',
        'subcategoria_set__inventario_set__datos_complementarios'
    )

    # Pasar las categorías al contexto
    return render(request, "inventarioGeneral.html", {
        "Categorias": categorias,
    })

#Vista solamente para el boton que dice "Ver Inventario General"
'''verInventarioGeneral

Similar a inventario_general, pero específicamente diseñado para una vista que muestra un inventario general con las mismas relaciones y optimizaciones.
Sirve como vista para el botón "Ver Inventario General".'''
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

'''editarInventario

Permite editar un ítem específico del inventario junto con sus relaciones (DetalleTecnico y DatosComplementarios).
Valida que los campos obligatorios (nombre, cantidad_disponible, y vencimiento, si se proporciona) sean correctos y consistentes.
Verifica que el nuevo nombre no esté duplicado en el inventario general.
Asegura que la cantidad disponible sea un número mayor o igual a 0.
Usa transaction.atomic() para garantizar la consistencia en las actualizaciones.
Actualiza los datos del inventario y sus relaciones, mostrando mensajes de éxito o error según corresponda.'''
@never_cache 
def editarInventario(request, id_inventario):
    # Obtiene el objeto del inventario y sus relaciones
    inventario = get_object_or_404(Inventario, id_inventario=id_inventario)
    detalle_tecnico = get_object_or_404(DetalleTecnico, inventario=inventario)
    datos_complementarios = get_object_or_404(DatosComplementarios, inventario=inventario)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Validar y actualizar nombre tanto si esta vacio como si esta repetido
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

                # Validar y actualizar cantidad_disponible, campo siempre debe existir y ser igual a 0 o mayor
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

                # Validar y actualizar vencimiento que se envie de forma aceptada por el navegador (formato correcto)
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

'''eliminarInventario

Permite eliminar un ítem específico del inventario.
Elimina en cascada las relaciones asociadas (DetalleTecnico y DatosComplementarios).
Muestra un mensaje de éxito si la eliminación se realiza correctamente o un mensaje de error si ocurre algún problema.'''
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

#Guardar Inventario General pasado
@login_required
@user_passes_test(lambda u: u.is_superuser)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def guardar_inventario_general(request):
    if request.method == 'POST':
        descripcion_usuario = request.POST.get('descripcion', '').strip()
        fecha_hora_actual = localtime(now())
        
        # Si el usuario no escribió nada, usamos la descripción automática
        if not descripcion_usuario:
            descripcion_usuario = f"Sin descripción."
        
        GuardadoInventarioGeneral.objects.create(
            descripcion=descripcion_usuario,
            fecha_guardado=fecha_hora_actual,
            usuario=request.user
        )
        
        messages.success(request, "¡Inventario general guardado exitosamente!")
        return redirect('inventario_general')
    
    return redirect('inventario_general')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def historial_inventario_general(request):
    historiales = GuardadoInventarioGeneral.objects.all().order_by('-fecha_guardado')
    return render(request, "historial_inventario_general.html", {"historiales": historiales})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def detalle_inventario_guardado(request, pk):
    inventario_guardado = get_object_or_404(GuardadoInventarioGeneral, pk=pk)
    return render(request, "detalle_inventario_guardado.html", {"inventario_guardado": inventario_guardado})


