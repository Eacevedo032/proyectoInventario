from django.shortcuts import render, redirect, get_object_or_404  # Añadir get_object_or_404 aquí
from django.contrib import messages
from aplicaciones.appGestionLaboratorios.models import SolicitudProductosInventario
from inventario_nuevo.models import Producto, Categoria, Subcategoria
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation  # Añadir para manejo de decimales
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo, convertir_unidades

@login_required
def solicitar_productos(request):
    # Procesamiento del formulario
    if request.method == 'POST':
        try:
            with transaction.atomic():
                fecha_reserva = request.POST.get('fecha_reserva')
                motivo = request.POST.get('motivo')
                
                # Verificar que tenemos datos de items (manteniendo los nombres originales de campos)
                items = request.POST.getlist('item[]')
                cantidades = request.POST.getlist('cantidad[]')
                unidades = request.POST.getlist('unidad_medida[]')
                
                if not fecha_reserva or not motivo or not items:
                    raise ValueError("Faltan datos obligatorios.")
                
                for i in range(len(items)):
                    producto = get_object_or_404(Producto, id=items[i])
                    
                    try:
                        cantidad_utilizada_decimal = Decimal(cantidades[i])
                        if cantidad_utilizada_decimal <= 0:
                            raise ValueError("La cantidad a utilizar debe ser mayor a 0.")
                    except (InvalidOperation, IndexError, TypeError):
                        raise ValueError("La cantidad ingresada no es válida.")
                    
                    unidad_medida = unidades[i]
                    unidad_producto = producto.unidad_medida.abreviatura if hasattr(producto.unidad_medida, 'abreviatura') else str(producto.unidad_medida)

                    # Manejo especial para unidades equivalentes
                    unidades_equivalentes = {
                        'unidad': ['unidad', 'unidades', 'unidad'],
                        'kg': ['kg', 'kilogramo', 'kilogramos'],
                        'g': ['g', 'gramo', 'gramos'],
                        'l': ['l', 'litro', 'litros'],
                    }

                    # Verificar si las unidades son equivalentes
                    unidades_compatibles = False
                    for grupo in unidades_equivalentes.values():
                        if (str(unidad_medida).lower() in grupo and 
                            str(unidad_producto).lower() in grupo):
                            unidades_compatibles = True
                            break

                    if unidades_compatibles:
                        cantidad_convertida = cantidad_utilizada_decimal
                    else:
                        try:
                            cantidad_convertida = convertir_unidades(
                                cantidad_utilizada_decimal, 
                                unidad_medida, 
                                unidad_producto
                            )
                        except ValueError as e:
                            raise ValueError(
                                f"No se pueden convertir {unidad_medida} a {unidad_producto}. "
                                "Solicite items cuyas unidades de medida sean compatibles."
                            )

                    # Verificación de disponibilidad
                    if cantidad_convertida > producto.cantidad_disponible:
                        raise ValueError(
                            f"La cantidad solicitada ({cantidad_convertida} {unidad_producto}) "
                            f"es mayor a la existente en Inventario ({producto.cantidad_disponible} {unidad_producto})."
                        )

                    # Creación del registro
                    SolicitudProductosInventario.objects.create(
                        usuario=request.user,
                        producto=producto,
                        cantidad_utilizada=cantidad_convertida,
                        unidad_medida=unidad_medida,
                        fecha_uso=fecha_reserva,
                        motivo=motivo,
                        estado=SolicitudProductosInventario.PENDIENTE,
                        cantidad_disponible_momento=producto.cantidad_disponible,
                        unidad_medida_momento=producto.unidad_medida,
                    )
            
            messages.success(request, 'Solicitud enviada correctamente.')
            return redirect('solicitar_productos')
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            print("Error completo:", str(e))
            if hasattr(e, '__traceback__'):
                import traceback
                traceback.print_exc()
    
    # Resto del código para GET requests
    todas_solicitudes = SolicitudProductosInventario.objects.filter(
        usuario=request.user
    ).order_by('-fecha_uso').select_related('producto')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(todas_solicitudes, 10)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'categorias': Categoria.objects.all(),
        'solicitudes_pendientes': todas_solicitudes.filter(estado='pendiente').count(),
        'solicitudes_aprobadas': todas_solicitudes.filter(estado='aprobada').count(),
        'solicitudes_rechazadas': todas_solicitudes.filter(estado='rechazada').count(),
        'page_obj': page_obj,
    }
    
    return render(request, 'solicitar_productos.html', context)

@login_required
def enviar_productos(request, producto_id):
    solicitud = get_object_or_404(SolicitudProductosInventario, id=producto_id, usuario=request.user)

    if solicitud.estado != SolicitudProductosInventario.PENDIENTE:
        messages.error(request, "Solo se pueden enviar solicitudes en estado pendiente.")
        return redirect('solicitar_productos')

    # Cambiar estado a "en revisión"
    solicitud.estado = SolicitudProductosInventario.EN_REVISION
    solicitud.save()
    
    messages.success(request, "La solicitud ha sido enviada y está en revisión.")
    return redirect('solicitar_productos')

@login_required
def editar_productos(request, producto_id):
    solicitud = get_object_or_404(
        SolicitudProductosInventario,
        id=producto_id,
        usuario=request.user,
        estado=SolicitudProductosInventario.PENDIENTE
    )

    if request.method == 'POST':
        try:
            with transaction.atomic():
                nueva_fecha = request.POST.get('fecha_reserva')
                nuevo_motivo = request.POST.get('motivo')
                nueva_cantidad = request.POST.get('cantidad').replace(',', '.')
                nueva_unidad = request.POST.get('unidad_medida')

                if not nueva_fecha or not nuevo_motivo or not nueva_cantidad:
                    raise ValueError("Todos los campos son obligatorios.")

                try:
                    nueva_cantidad_decimal = Decimal(nueva_cantidad)
                    if nueva_cantidad_decimal <= 0:
                        raise ValueError("La cantidad debe ser mayor a cero.")
                except InvalidOperation:
                    raise ValueError("Cantidad inválida.")

                producto = solicitud.producto
                unidad_producto = producto.unidad_medida.abreviatura if hasattr(producto.unidad_medida, 'abreviatura') else str(producto.unidad_medida)

                unidades_equivalentes = {
                    'unidad': ['unidad', 'unidades', 'unidad'],
                    'kg': ['kg', 'kilogramo', 'kilogramos'],
                    'g': ['g', 'gramo', 'gramos'],
                    'l': ['l', 'litro', 'litros'],
                }

                unidades_compatibles = any(
                    str(nueva_unidad).lower() in grupo and str(unidad_producto).lower() in grupo
                    for grupo in unidades_equivalentes.values()
                )

                if unidades_compatibles:
                    cantidad_convertida = nueva_cantidad_decimal
                else:
                    try:
                        cantidad_convertida = convertir_unidades(
                            nueva_cantidad_decimal, nueva_unidad, unidad_producto
                        )
                    except ValueError:
                        raise ValueError(
                            f"No se puede convertir {nueva_unidad} a {unidad_producto}. Use unidades compatibles."
                        )

                if cantidad_convertida > producto.cantidad_disponible:
                    raise ValueError(
                        f"Cantidad solicitada ({cantidad_convertida} {unidad_producto}) "
                        f"mayor a disponible ({producto.cantidad_disponible} {unidad_producto})."
                    )

                solicitud.fecha_uso = nueva_fecha
                solicitud.motivo = nuevo_motivo
                solicitud.cantidad_utilizada = str(cantidad_convertida).replace(",", ".")
                solicitud.unidad_medida = nueva_unidad
                solicitud.save()

                messages.success(request, "Solicitud actualizada correctamente.")
                return redirect('solicitar_productos')

        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")

        # Obtener la unidad de medida actual de la solicitud
    unidad_actual = solicitud.unidad_medida

    return render(request, 'editar_productos.html', {'solicitud': solicitud, 'unidad_actual': unidad_actual})

@login_required
def eliminar_productos(request, producto_id):
    # Obtener la solicitud de producto
    producto_id = get_object_or_404(SolicitudProductosInventario, id=producto_id)
    
    # Verificar si la solicitud está en estado "pendiente" o "rechazada"
    if producto_id.estado not in ['pendiente', 'rechazada']:
        messages.error(request, "Solo se pueden eliminar solicitudes pendientes o rechazadas.")
        return redirect('solicitar_productos')
    
    # Eliminar la solicitud
    producto_id.delete()
    messages.success(request, "La solicitud ha sido eliminada correctamente.")
    
    return redirect('solicitar_productos')

# Vista para AJAX que necesitarás para los selects anidados
@login_required
def get_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = Subcategoria.objects.filter(categoria_id=categoria_id).values('id', 'nombre')
    return JsonResponse(list(subcategorias), safe=False)

@login_required
def get_productos(request):
    subcategoria_id = request.GET.get('subcategoria_id')
    productos = Producto.objects.filter(subcategoria_id=subcategoria_id).values('id', 'nombre')
    return JsonResponse(list(productos), safe=False)