from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
import os
from django.conf import settings
from weasyprint import HTML
from django.templatetags.static import static
from django.urls import reverse

from inventario_nuevo.models import (
    InventarioFisicoDetalle, InventarioFisico,
    HistorialInventarioFisico, Producto, TransferenciaProducto
)

# Decorador para restringir acceso solo a "administrador"
def solo_administrador(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.username != "administrador":
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return redirect('lista_inventarios_pendientes')  # o donde quieras redirigir
        return view_func(request, *args, **kwargs)
    return wrapper

def registrar_inventario_fisico(request):
    productos = Producto.objects.exclude(estado__estado='baja')  # Excluir productos dados de baja
    hay_inventario_pendiente = InventarioFisico.objects.filter(estado='pendiente').exists()

    if request.method == 'POST':
        if hay_inventario_pendiente:
            messages.warning(request, "⚠️ Hay un inventario pendiente. No puedes crear otro hasta ejecutarlo o cancelarlo.")
            return redirect('registrar_inventario_fisico')

        inventario = InventarioFisico.objects.create(
            fecha=timezone.now().date(),
            estado='pendiente',
            creado_por=request.user,
        )

        for producto in productos:
            cantidad_final_str = request.POST.get(f'cantidad_{producto.id}')
            motivo_modificacion = request.POST.get(f'motivo_{producto.id}', '')  # Obtener el motivo del formulario
            
            if cantidad_final_str is None:
                continue

            try:
                cantidad_final = Decimal(cantidad_final_str)
            except (InvalidOperation, TypeError):
                cantidad_final = Decimal(producto.cantidad_disponible)

            if cantidad_final > Decimal('999999999.99') or cantidad_final < Decimal('0'):
                messages.error(request, f"Cantidad inválida para el producto {producto.nombre}. Máximo permitido: 999999999.99")
                continue

            cantidad_inicial = Decimal(producto.cantidad_disponible)
            diferencia = cantidad_final - cantidad_inicial

            if diferencia != 0:
                # Solo creamos el detalle del inventario aquí
                InventarioFisicoDetalle.objects.create(
                    inventario=inventario,
                    producto=producto,
                    cantidad_inicial=cantidad_inicial,
                    cantidad_final=cantidad_final,
                    diferencia=diferencia,
                    motivo_modificacion=motivo_modificacion  # Guardamos el motivo en el detalle
                )
                
                # NO creamos el registro en el historial aquí todavía
                # El historial se creará solo al ejecutar el inventario

        messages.success(request, "Inventario físico registrado y pendiente de aprobación.")
        return redirect('lista_inventarios_pendientes')

    return render(request, 'inventario_nuevo/registrar_inventario.html', {
        'productos': productos,
        'inventario_ejecutado': not hay_inventario_pendiente,
        'fecha_actual': timezone.now()
    })

def lista_inventarios_pendientes(request):
    inventarios = InventarioFisico.objects.filter(estado='pendiente')\
        .select_related('creado_por')\
        .prefetch_related(
            'detalles__producto__ubicacion',
            'detalles__producto__categoria',
            'detalles__producto__subcategoria'
        )
    
    # Elimina el bucle que busca en el historial, ya no es necesario
    return render(request, 'inventario_nuevo/lista_inventarios_pendientes.html', {'inventarios': inventarios})

def ver_detalle_inventario(request, inventario_id):
    inventario = get_object_or_404(InventarioFisico, id=inventario_id, estado='pendiente')
    detalles = inventario.detalles.all()
    return render(request, 'inventario_nuevo/detalle_inventario.html', {'inventario': inventario, 'detalles': detalles})

@solo_administrador
def ejecutar_inventario_fisico(request, inventario_id):
    inventario = get_object_or_404(InventarioFisico, id=inventario_id, estado='pendiente')

    if request.method == 'POST':
        detalles = inventario.detalles.all()
        for detalle in detalles:
            # Verificar si ya existe un registro en el historial para este detalle
            historial_existente = HistorialInventarioFisico.objects.filter(
                inventario=inventario,
                producto=detalle.producto,
                fecha_aprobacion__isnull=True
            ).exists()
            
            if not historial_existente:
                producto = detalle.producto
                producto.cantidad_disponible = detalle.cantidad_final
                producto.save()

                HistorialInventarioFisico.objects.create(
                    inventario=inventario,
                    producto=producto,
                    cantidad_inicial=detalle.cantidad_inicial,
                    cantidad_final=detalle.cantidad_final,
                    diferencia=detalle.diferencia,
                    usuario=request.user,
                    fecha_aprobacion=timezone.now(),
                    motivo_modificacion=detalle.motivo_modificacion
                )

        inventario.estado = 'ejecutado'
        inventario.save()
        messages.success(request, "Inventario ejecutado correctamente.")
        return redirect('lista_inventarios_pendientes')

    return render(request, 'inventario_nuevo/confirmar_ejecucion.html', {'inventario': inventario})

@solo_administrador
def ejecutar_todo_inventario_fisico(request):
    if request.method == 'POST':
        inventarios_pendientes = InventarioFisico.objects.filter(estado='pendiente')
        for inventario in inventarios_pendientes:
            detalles = inventario.detalles.all()
            for detalle in detalles:
                # Verificar si ya existe un registro en el historial para este detalle
                historial_existente = HistorialInventarioFisico.objects.filter(
                    inventario=inventario,
                    producto=detalle.producto,
                    fecha_aprobacion__isnull=True
                ).exists()
                
                if not historial_existente:
                    producto = detalle.producto
                    producto.cantidad_disponible = detalle.cantidad_final
                    producto.save()

                    HistorialInventarioFisico.objects.create(
                        inventario=inventario,
                        producto=detalle.producto,
                        cantidad_inicial=detalle.cantidad_inicial,
                        cantidad_final=detalle.cantidad_final,
                        diferencia=detalle.diferencia,
                        usuario=request.user,
                        fecha_aprobacion=timezone.now(),
                        motivo_modificacion=detalle.motivo_modificacion
                    )
            inventario.estado = 'ejecutado'
            inventario.save()
        messages.success(request, "Todos los inventarios pendientes se ejecutaron correctamente.")
    return redirect('lista_inventarios_pendientes')

@solo_administrador
def editar_inventario_pendiente(request, inventario_id):
    inventario = get_object_or_404(InventarioFisico, id=inventario_id, estado='pendiente')
    detalles = InventarioFisicoDetalle.objects.filter(inventario=inventario)

    if request.method == 'POST':
        cambios_realizados = False

        for detalle in detalles:
            key_cantidad = f'cantidad_final_{detalle.id}'
            key_motivo = f'motivo_{detalle.id}'
            
            if key_cantidad in request.POST:
                try:
                    cantidad_final_nueva = Decimal(request.POST[key_cantidad])
                    motivo = request.POST.get(key_motivo, detalle.motivo_modificacion or '')  # Mantiene el motivo existente si no se proporciona uno nuevo
                    
                    if cantidad_final_nueva != detalle.cantidad_final:
                        diferencia = cantidad_final_nueva - detalle.cantidad_inicial

                        # Solo crear historial si hay cambio en cantidad
                        HistorialInventarioFisico.objects.create(
                            inventario=inventario,
                            producto=detalle.producto,
                            cantidad_inicial=detalle.cantidad_inicial,
                            cantidad_final=cantidad_final_nueva,
                            diferencia=diferencia,
                            usuario=request.user,
                            fecha_registro=timezone.now(),
                            motivo_modificacion=motivo
                        )

                        # Actualizar detalle
                        detalle.cantidad_final = cantidad_final_nueva
                        detalle.diferencia = diferencia
                        detalle.motivo_modificacion = motivo  # Actualizar motivo siempre
                        detalle.save()
                        cambios_realizados = True
                        
                except (InvalidOperation, ValueError):
                    pass

        if cambios_realizados:
            messages.success(request, "Inventario actualizado y cambios registrados en el historial.")
        else:
            messages.info(request, "No se detectaron cambios.")

        return redirect('ver_detalle_inventario', inventario.id)

    return render(request, 'inventario_nuevo/editar_inventario_pendiente.html', {
        'inventario': inventario,
        'detalles': detalles,
        'now': timezone.now(),
    })

@solo_administrador
def cancelar_conteo(request):
    if request.method == 'POST':
        pendientes = InventarioFisico.objects.filter(estado='pendiente')
        pendientes.update(estado='rechazado')
        messages.success(request, "Conteo cancelado y todos los inventarios pendientes rechazados.")
    return redirect('lista_inventarios_pendientes')

@solo_administrador
def eliminar_inventario_pendiente(request, detalle_id):
    detalle = get_object_or_404(InventarioFisicoDetalle, id=detalle_id)
    try:
        detalle.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Detalle eliminado correctamente.')
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, 'Error al eliminar el detalle.')
    return redirect('lista_inventarios_pendientes')

def historial_inventario_fisico(request):
    # Filtramos solo registros ejecutados (con fecha_aprobacion)
    historial = HistorialInventarioFisico.objects.filter(
        fecha_aprobacion__isnull=False
    ).select_related(
        'producto', 
        'usuario', 
        'inventario',
        'producto__categoria',
        'producto__subcategoria',
        'producto__unidad_medida'
    ).order_by('-fecha_aprobacion')  # Ordenamos por fecha de ejecución

    # Filtros
    usuario = request.GET.get('usuario')
    producto = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_movimiento = request.GET.get('tipo_movimiento')

    if usuario:
        historial = historial.filter(usuario_id=usuario)
    if producto:
        historial = historial.filter(producto_id=producto)
    if fecha_inicio:
        historial = historial.filter(fecha_aprobacion__gte=fecha_inicio)
    if fecha_fin:
        historial = historial.filter(fecha_aprobacion__lte=fecha_fin)
    if tipo_movimiento:
        if tipo_movimiento == 'positivo':
            historial = historial.filter(diferencia__gt=0)
        elif tipo_movimiento == 'negativo':
            historial = historial.filter(diferencia__lt=0)
        elif tipo_movimiento == 'cero':
            historial = historial.filter(diferencia=0)

    # Paginación
    paginator = Paginator(historial, 10)  # 20 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Datos para filtros
    usuarios = User.objects.filter(
        id__in=historial.values_list('usuario_id', flat=True).distinct()
    )
    productos = Producto.objects.filter(
        id__in=historial.values_list('producto_id', flat=True).distinct()
    )

    context = {
        'page_obj': page_obj,
        'usuarios': usuarios,
        'productos': productos,
        'filtros': request.GET,
    }
    return render(request, 'inventario_nuevo/historial_inventario_fisico.html', context)

def exportar_historial_pdf(request):
    filtros = {
        "usuario": request.GET.get("usuario", ""),
        "producto": request.GET.get("producto", ""),
        "fecha_inicio": request.GET.get("fecha_inicio", ""),
        "fecha_fin": request.GET.get("fecha_fin", ""),
    }

    historial = HistorialInventarioFisico.objects.select_related(
        'producto', 'usuario', 'inventario'
    ).all().order_by('-fecha_registro')

    if filtros["usuario"]:
        historial = historial.filter(usuario_id=filtros["usuario"])
    if filtros["producto"]:
        historial = historial.filter(producto_id=filtros["producto"])
    if filtros["fecha_inicio"]:
        historial = historial.filter(fecha_modificacion__date__gte=filtros["fecha_inicio"])
    if filtros["fecha_fin"]:
        historial = historial.filter(fecha_modificacion__date__lte=filtros["fecha_fin"])

    filtros_aplicados = {}
    if filtros["usuario"]:
        try:
            usuario = User.objects.get(id=filtros["usuario"])
            filtros_aplicados["Usuario"] = usuario.username
        except User.DoesNotExist:
            filtros_aplicados["Usuario"] = "Desconocido"
    if filtros["producto"]:
        try:
            producto = Producto.objects.get(id=filtros["producto"])
            filtros_aplicados["Producto"] = producto.nombre
        except Producto.DoesNotExist:
            filtros_aplicados["Producto"] = "Desconocido"
    if filtros["fecha_inicio"]:
        filtros_aplicados["Fecha desde"] = filtros["fecha_inicio"]
    if filtros["fecha_fin"]:
        filtros_aplicados["Fecha hasta"] = filtros["fecha_fin"]

    # Genera URL completa para la imagen del logo, para que WeasyPrint la pueda cargar
    logo_url = request.build_absolute_uri(static('img/logoUNP1.png'))

    context = {
        'historial': historial,
        'usuario_generador': request.user.username,
        'fecha_actual': timezone.now(),
        'logo_url': logo_url,
        'filtros_aplicados': filtros_aplicados,
    }

    template = get_template('inventario_nuevo/historial_inventario_pdf.html')
    html_string = template.render(context)

    # Generar PDF con WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf(stylesheets=None)  # Puedes añadir estilos aquí

    response = HttpResponse(pdf_file, content_type='application/pdf')
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f'historial_inventario_{fecha_actual}.pdf'
    response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'

    return response







#TRANSFERENCIA REGISTRA Y ACTUALIZA
def transferencia_producto(request):
    productos = Producto.objects.all()
    estados = ["Dado de baja", "Mantenimiento", "No Disponible", "Prestado", "Ingreso"]

    if request.method == 'POST':
        producto = Producto.objects.get(id=request.POST.get('producto_id'))
        estado_destino = request.POST.get('estado')
        cantidad_transferida = Decimal(request.POST.get('cantidad', 0))  #Convierte a Decimal
        usuario = request.user  #Captura el usuario autenticado
        motivo = request.POST.get('motivo', '')

        #Ajuste automático del inventario
        inventario, created = InventarioFisico.objects.get_or_create(producto=producto, fecha=timezone.now().date())

        if estado_destino == "Ingreso":
            inventario.cantidad_final += cantidad_transferida  #Aumenta cantidad
        else:
            inventario.cantidad_final -= cantidad_transferida  #Reduce cantidad
        
        inventario.calcular_diferencia()  #Calcula la diferencia correctamente
        inventario.save()

        #egistrar la transferencia en el historial
        TransferenciaProducto.objects.create(
            producto=producto,
            usuario=usuario, 
            estado_destino=estado_destino,
            cantidad=cantidad_transferida,
            motivo=motivo,
            fecha_transferencia=timezone.now().date()
        )

        return redirect(reverse('historial_transferencias'))  #Redirige al historial

    return render(request, 'inventario_nuevo/transferencia_producto.html', {'productos': productos, 'estados': estados})

def historial_transferencias(request):
    transferencias = TransferenciaProducto.objects.all().order_by('-fecha_transferencia')
    return render(request, 'inventario_nuevo/historial_transferencias.html', {'transferencias': transferencias})

