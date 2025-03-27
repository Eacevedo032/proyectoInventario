from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from datetime import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required,  user_passes_test
from aplicaciones.appGestionInventario.models import Categoria, SubCategoria, Inventario, DetalleTecnico, DatosComplementarios
from aplicaciones.appGestionInventario.models import GuardadoInventarioGeneral, CategoriaSubcategoriaSnapshot, InventarioGuardado
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.core.paginator import Paginator

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
@transaction.atomic
def guardar_inventario_general(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', 'Sin nombre')
        descripcion_usuario = request.POST.get('descripcion', 'Sin descripción').strip()
        
        # Crear snapshot principal
        guardado = GuardadoInventarioGeneral.objects.create(
            nombre=nombre,
            descripcion=descripcion_usuario,
            usuario=request.user
        )
        
        # Copiar estructura completa con prefetch para optimizar
        categorias = Categoria.objects.all().prefetch_related(
            Prefetch('subcategoria_set', 
                   queryset=SubCategoria.objects.all().prefetch_related(
                       Prefetch('inventario_set',
                              queryset=Inventario.objects.select_related(
                                  'detalle_tecnico',
                                  'datos_complementarios'
                              )
                       )
                   )
            )
        )
        
        for categoria in categorias:
            subcategorias = categoria.subcategoria_set.all()
            
            if not subcategorias.exists():
                # Guardar categoría sin subcategorías
                cat_snapshot = CategoriaSubcategoriaSnapshot.objects.create(
                    guardado=guardado,
                    nombre_categoria=categoria.nombre_categoria,
                    descripcion_categoria=categoria.descripcion,
                    nombre_subcategoria="SIN SUBCATEGORÍAS"
                )
            else:
                for subcategoria in subcategorias:
                    # Guardar subcategoría
                    cat_snapshot = CategoriaSubcategoriaSnapshot.objects.create(
                        guardado=guardado,
                        nombre_categoria=categoria.nombre_categoria,
                        descripcion_categoria=categoria.descripcion,
                        nombre_subcategoria=subcategoria.nombre
                    )
                    
                    # Copiar todos los ítems con manejo seguro de campos relacionados
                    for item in subcategoria.inventario_set.all():
                        InventarioGuardado.objects.create(
                            categoria_subcategoria=cat_snapshot,
                            # Campos básicos
                            nombre=item.nombre,
                            descripcion=item.descripcion,
                            cantidad_disponible=item.cantidad_disponible,
                            unidad_medida=item.unidad_medida,
                            lote=item.lote,
                            vencimiento=item.vencimiento,
                            observaciones=item.observaciones,
                            # Campos técnicos (con manejo de relaciones)
                            marca_caracteristica=getattr(item.detalle_tecnico, 'marca_caracteristica', ''),
                            num_cat=getattr(item.detalle_tecnico, 'num_cat', ''),
                            num_serie=getattr(item.detalle_tecnico, 'num_serie', ''),
                            modelo=getattr(item.detalle_tecnico, 'modelo', ''),
                            codigo=getattr(item.detalle_tecnico, 'codigo', ''),
                            articulo=getattr(item.detalle_tecnico, 'articulo', ''),
                            # Datos complementarios
                            presentacion=getattr(item.datos_complementarios, 'presentacion', ''),
                            accesorios=getattr(item.datos_complementarios, 'accesorios', ''),
                            medidas=getattr(item.datos_complementarios, 'medidas', ''),
                            colores=getattr(item.datos_complementarios, 'colores', ''),
                            capacidad=getattr(item.datos_complementarios, 'capacidad', ''),
                            informacionAdicional=getattr(item.datos_complementarios, 'informacionAdicional', '')
                        )
        
        messages.success(request, "¡Inventario General guardado correctamente!")
        return redirect('historial_inventario_general')
    
    return redirect('verInventarioGuardar')

#Paginación para mejor orden
@login_required
@user_passes_test(lambda u: u.is_superuser)
def historial_inventario_general(request):
    historiales = GuardadoInventarioGeneral.objects.all().order_by('-fecha_guardado')
    paginator = Paginator(historiales, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "historial_inventario_general.html", {
        "page_obj": page_obj,
        "historiales": page_obj.object_list  # Nueva variable para el exporte
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def detalle_inventario_guardado(request, pk):
    inventario_guardado = get_object_or_404(GuardadoInventarioGeneral, pk=pk)
    
    # Obtener categorías-subcategorías con sus ítems (usando el nombre correcto de la relación)
    categorias_subcategorias = CategoriaSubcategoriaSnapshot.objects.filter(
        guardado=inventario_guardado
    ).prefetch_related(
        'items_snapshot' 
    )
    
    # Organizar los datos
    categorias_organizadas = {}
    for cs in categorias_subcategorias:
        if cs.nombre_categoria not in categorias_organizadas:
            categorias_organizadas[cs.nombre_categoria] = {
                'descripcion': cs.descripcion_categoria,
                'subcategorias': {}
            }
        
        # Agregar subcategoría con sus ítems (accediendo a items_snapshot)
        categorias_organizadas[cs.nombre_categoria]['subcategorias'][cs.nombre_subcategoria] = list(
            cs.items_snapshot.all()  #Relación correcta
        )
    
    context = {
        'inventario_guardado': inventario_guardado,
        'categorias_organizadas': categorias_organizadas
    }
    
    return render(request, "detalle_inventario_guardado.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser) # Permite el acceso solo a usuarios con privilegios de superusuario (administradores).
def eliminarInventarioGuardado(request, id_guardado):
    try:
        # Obtiene el objeto del guardado usando 'id' se usa simplemente para referirse al objeto que se encontró, podría ser otro nombre incluso
        guardado = get_object_or_404(GuardadoInventarioGeneral, id=id_guardado) # get_object_or_404: Busca el objeto GuardadoInventarioGeneral con el id igual a id_guardado, sino devuelve un error 404

        # Elimina el guardado, aplicando el borrado en cascada si está configurado en el modelo
        guardado.delete()
        messages.success(request, "¡Inventario guardado eliminado exitosamente!")
    except Exception as e:
        messages.error(request, f"Error al eliminar el inventario guardado: {e}")

    return redirect("historial_inventario_general")

#Vista del Inventario General donde estarán las opciones de las vistas de arriba (guardar inventario y ver historial de inventarios guardados)
def verInventarioGuardar(request):
    # Cargar categorías con sus subcategorías e ítems (incluyendo las tablas (clases) relacionadas)
    categorias = Categoria.objects.prefetch_related( #prefetch_related asegura que todos los datos relacionados se carguen de manera eficiente, evitando múltiples consultas innecesarias
        'subcategoria_set__inventario_set__detalle_tecnico',
        'subcategoria_set__inventario_set__datos_complementarios'
    )

    # Pasar las categorías al contexto
    return render(request, "verInventarioGuardar.html", {
        "Categorias": categorias,
    })
#----------------------------------------------------------------------------
#EXPORTAR HISTORIAL DE INVENTARIOS GUARDADOS

#EXPORTAR A EXCEL PRIMERO

from django.db.models import Prefetch
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def exportar_inventario_excel(request, pk):
    inventario = get_object_or_404(GuardadoInventarioGeneral, pk=pk)
    
    # Obtener todas las categorías/subcategorías con sus ítems relacionados
    categorias = CategoriaSubcategoriaSnapshot.objects.filter(
        guardado=inventario
    ).order_by('nombre_categoria', 'nombre_subcategoria').prefetch_related(
        Prefetch('items_snapshot', queryset=InventarioGuardado.objects.all())
    )
    
    # Estructura de datos completa
    data = []
    for cat in categorias:
        # Caso 1: Categoría sin subcategorías
        if cat.nombre_subcategoria == "SIN SUBCATEGORÍAS":
            data.append({
                'Categoría': cat.nombre_categoria,
                'Subcategoría': 'SIN SUBCATEGORÍAS',
                'Item': 'SIN ÍTEMS',
                'Descripción': '',
                'Cantidad': '',
                'Unidad': '',
                'Lote': '',
                'Vencimiento': '',
                'Observaciones': '',
                'N° Serie': '',
                'Marca': '',
                'Artículo': '',
                'Color': '',
                'Modelo': '',
                'Código': '',
                'Presentación': '',
                'Accesorios': '',
                'Medidas': '',
                'Capacidad': '',
                'Información Adicional': ''
            })
        else:
            # Caso 2: Subcategoría sin ítems
            if not cat.items_snapshot.exists():
                data.append({
                    'Categoría': cat.nombre_categoria,
                    'Subcategoría': cat.nombre_subcategoria,
                    'Item': 'SIN ÍTEMS',
                    'Descripción': '',
                    'Cantidad': '',
                    'Unidad': '',
                    'Lote': '',
                    'Vencimiento': '',
                    'Observaciones': '',
                    'N° Serie': '',
                    'Marca': '',
                    'Artículo': '',
                    'Color': '',
                    'Modelo': '',
                    'Código': '',
                    'Presentación': '',
                    'Accesorios': '',
                    'Medidas': '',
                    'Capacidad': '',
                    'Información Adicional': ''
                })
            # Caso 3: Subcategoría con ítems
            for item in cat.items_snapshot.all():
                data.append({
                    'Categoría': cat.nombre_categoria,
                    'Subcategoría': cat.nombre_subcategoria,
                    'Item': item.nombre,
                    'Descripción': item.descripcion or '-',
                    'Cantidad': item.cantidad_disponible,
                    'Unidad': item.unidad_medida or '-',
                    'Lote': item.lote or '-',
                    'Vencimiento': item.vencimiento.strftime('%d/%m/%Y') if item.vencimiento else '-',
                    'Observaciones': item.observaciones or '-',
                    'N° Serie': item.num_serie or '-',
                    'Marca': item.marca_caracteristica or '-',
                    'Artículo': item.articulo or '-',
                    'Color': item.colores or '-',
                    'Modelo': item.modelo or '-',
                    'Código': item.codigo or '-',
                    'Presentación': item.presentacion or '-',
                    'Accesorios': item.accesorios or '-',
                    'Medidas': item.medidas or '-',
                    'Capacidad': item.capacidad or '-',
                    'Información Adicional': item.informacionAdicional or '-'
                })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Generar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Inventario', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Inventario']
        
        # Autoajustar columnas
        for column in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in column)
            adjusted_width = (max_length + 2) if max_length < 50 else 50
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=Inventario_{inventario.nombre}.xlsx'
    return response

# EXPORTAR A PDF

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from django.utils.timezone import localtime
import pytz

@login_required
def exportar_inventario_pdf(request, pk):
    inventario = get_object_or_404(GuardadoInventarioGeneral, pk=pk)
    
    # Obtener todas las categorías/subcategorías con sus ítems
    categorias = CategoriaSubcategoriaSnapshot.objects.filter(
        guardado=inventario
    ).order_by('nombre_categoria', 'nombre_subcategoria').prefetch_related(
        'items_snapshot'
    )
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inventario_{inventario.nombre}.pdf'
    
    # Configuración horizontal con márgenes reducidos
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    styles.add(ParagraphStyle(
        name='TitleCentered',
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=15,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='CategoryHeader',
        fontSize=11,
        textColor=colors.HexColor('#3498db'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    # Fecha local corregida para Nicaragua
    tz = pytz.timezone('America/Managua')
    fecha_local = localtime(inventario.fecha_guardado, timezone=tz)
    
    # Título principal
    elements.append(Paragraph(f"INVENTARIO: {inventario.nombre}", styles['TitleCentered']))
    elements.append(Paragraph(
        f"Fecha: {fecha_local.strftime('%d/%m/%Y %H:%M')} (Hora Nicaragua)", 
        ParagraphStyle(
            name='DateStyle',
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=15
        )
    ))
    elements.append(Spacer(1, 15))
    
    # Columnas a mostrar (puedes ajustar según necesidad)
    columnas = [
        'Subcategoría', 'Item', 'Descripción', 'Cantidad', 'Unidad',
        'Lote', 'Vencimiento', 'N° Serie', 'Marca', 'Artículo',
        'Color', 'Modelo', 'Código', 'Presentación'
    ]
    
    # Anchos de columna optimizados
    col_widths = [70, 80, 100, 40, 40, 50, 60, 60, 60, 50, 40, 50, 50, 70]
    
    # Por cada categoría
    for cat in categorias:
        # Encabezado de categoría
        elements.append(Paragraph(
            f"CATEGORÍA: {cat.nombre_categoria}",
            styles['CategoryHeader']
        ))
        
        # Tabla de ítems
        data = [columnas]  # Encabezados
        
        # Caso 1: Sin subcategorías
        if cat.nombre_subcategoria == "SIN SUBCATEGORÍAS":
            data.append(['SIN SUBCATEGORÍAS', 'SIN ÍTEMS'] + [''] * (len(columnas) - 2))
        else:
            # Caso 2: Subcategoría sin ítems
            if not cat.items_snapshot.exists():
                data.append([cat.nombre_subcategoria, 'SIN ÍTEMS'] + [''] * (len(columnas) - 2))
            # Caso 3: Subcategoría con ítems
            for item in cat.items_snapshot.all():
                data.append([
                    cat.nombre_subcategoria,
                    item.nombre,
                    item.descripcion or '-',
                    str(item.cantidad_disponible),
                    item.unidad_medida or '-',
                    item.lote or '-',
                    item.vencimiento.strftime('%d/%m/%Y') if item.vencimiento else '-',
                    item.num_serie or '-',
                    item.marca_caracteristica or '-',
                    item.articulo or '-',
                    item.colores or '-',
                    item.modelo or '-',
                    item.codigo or '-',
                    item.presentacion or '-'
                ])
        
        # Crear tabla para el PDF
        t = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla optimizado
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (1,1), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTSIZE', (0,1), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f9f9f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('WORDWRAP', (0,0), (-1,-1), True),
        ])
        
        # Alternar colores de fila
        for i in range(1, len(data)):
            bg_color = colors.white if i % 2 == 1 else colors.HexColor('#e9ecef')
            table_style.add('BACKGROUND', (0,i), (-1,i), bg_color)
        
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(1, 15))
    
    doc.build(elements)
    return response