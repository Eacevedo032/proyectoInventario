from django.utils import timezone
from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import Categoria, HistorialInventario, Inventario, SolicitudLaboratorio, SubCategoria, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.db import transaction

# Vista para solicitar una reservación de laboratorio y mostrar las solicitudes del usuario autenticado
@login_required 
def reservar_laboratorio(request):
    if request.method == 'POST':
        laboratorio = request.POST['laboratorio']
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']

        # Validación de hora
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect('reservar_laboratorio')

        # Crear solicitud
        solicitud = SolicitudLaboratorio(
            usuario=request.user,
            laboratorio=laboratorio,
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=SolicitudLaboratorio.PENDIENTE
        )
        solicitud.save()
        messages.success(request, 'La solicitud de reserva se ha creado exitosamente.')
        return redirect('reservar_laboratorio')

    # Obtener todas las solicitudes del usuario autenticado
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)
    
    return render(request, 'reservar_laboratorio.html', {'solicitudes': solicitudes})

# Vista para solicitar recursos desde una cuenta de usuario sin privilegios de administrador
@login_required
def solicitar_recursos(request):
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        inventario_id = request.POST.get('inventario')  # Cambiado a 'inventario'
        usuario_id = request.POST.get('usuario')
        cantidad_utilizada = request.POST.get('cantidad_utilizada')
        fecha_uso = request.POST.get('fecha_uso')

        # Crear instancia de UsoItemLaboratorio
        uso_item = UsoItemLaboratorio(
            solicitud_id=solicitud_id,
            inventario_id=inventario_id,  # Cambiado a 'inventario_id'
            usuario_id=usuario_id,
            cantidad_utilizada=cantidad_utilizada,
            fecha_uso=fecha_uso
        )
        uso_item.save()
        messages.success(request, 'La solicitud de recursos se ha creado exitosamente.')
        return redirect('solicitar_recursos')

    categorias = Categoria.objects.all()
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    solicitudes_recursos = UsoItemLaboratorio.objects.filter(
        usuario=request.user
    ).select_related('inventario', 'solicitud').order_by('solicitud__laboratorio')

    solicitudes_por_laboratorio = {
        laboratorio: list(items)
        for laboratorio, items in groupby(solicitudes_recursos, key=lambda x: x.solicitud.laboratorio)
    }

    return render(request, 'solicitar_recursos.html', {
        'solicitudes': solicitudes,
        'solicitudes_por_laboratorio': solicitudes_por_laboratorio,
        'categorias': categorias
    })

# Vista para obtener las subcategorías de una categoría específica
@login_required
def obtener_subcategorias(request, categoria_id):
    subcategorias = SubCategoria.objects.filter(categoria_id=categoria_id).values('id_subcategoria', 'nombre')
    subcategorias_list = list(subcategorias)
    return JsonResponse({'subcategorias': subcategorias_list})

# Vista para obtener los ítems de una subcategoría específica dentro de una categoría
@login_required 
def obtener_items(request, categoria_id, subcategoria_id=None):
    try:
        # Validar que la categoría existe
        categoria = Categoria.objects.get(id_categoria=categoria_id)
    except Categoria.DoesNotExist:
        return JsonResponse({'error': 'Categoría no encontrada'}, status=404)
    
    if subcategoria_id:
        try:
            subcategoria = SubCategoria.objects.get(id_subcategoria=subcategoria_id, categoria_id=categoria_id)
            items = Inventario.objects.filter(categoria_id=categoria_id, subcategoria_id=subcategoria_id).values('id_inventario', 'nombre', 'descripcion', 'cantidad_disponible')
        except SubCategoria.DoesNotExist:
            return JsonResponse({'error': 'Subcategoría no encontrada o no pertenece a la categoría'}, status=404)
    else:
        items = Inventario.objects.filter(categoria_id=categoria_id).values('id_inventario', 'nombre', 'descripcion', 'cantidad_disponible')

    items_list = list(items)
    return JsonResponse({'items': items_list})


#views solo para opciones de administrador
# Vista para administrar las solicitudes de laboratorio con ítems solicitados
def administracionLaboratorios(request):
    # Obtener todas las solicitudes junto con los ítems solicitados
    solicitudes = SolicitudLaboratorio.objects.select_related('usuario').order_by('usuario__username')
    
    # Diccionario para almacenar solicitudes agrupadas por usuario con sus ítems
    solicitudes_por_usuario = {}
    for usuario, solicitudes_usuario in groupby(solicitudes, lambda s: s.usuario):
        solicitudes_usuario_list = list(solicitudes_usuario)
        
        # Agregar los ítems solicitados para cada solicitud
        for solicitud in solicitudes_usuario_list:
            solicitud.items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)
        
        solicitudes_por_usuario[usuario] = solicitudes_usuario_list

    return render(request, 'administracionLaboratorios.html', {
        'solicitudes_por_usuario': solicitudes_por_usuario
    })

#para ver los recursos a utilizar en el laboratorio
def ver_items_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

    return render(request, 'ver_items_solicitud.html', {
        'solicitud': solicitud,
        'items_solicitados': items_solicitados
    })

# Vista para aprobar solicitudes y actualizar inventario
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    if solicitud.estado != 'aprobada':
        solicitud.estado = 'aprobada'

        with transaction.atomic():
            items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

            for item in items_solicitados:
                inventario_item = item.inventario  # Cambiado a 'inventario'

                if inventario_item.cantidad_disponible >= item.cantidad_utilizada:
                    inventario_item.cantidad_disponible -= item.cantidad_utilizada
                    inventario_item.save()

                    HistorialInventario.objects.create(
                        inventario=inventario_item,
                        cantidad_cambiada=item.cantidad_utilizada,
                        fecha_cambio=timezone.now(),
                        tipo_cambio='salida'
                    )
                else:
                    messages.error(request, f"No hay suficiente cantidad de {inventario_item.nombre} en inventario.")
                    return redirect('administracion_laboratorios')

            solicitud.save()
            messages.success(request, 'La solicitud ha sido aprobada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para rechazar solicitudes
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    solicitud.estado = 'rechazada'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido rechazada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para solicitudes pendientes
def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    solicitud.estado = 'pendiente'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido marcada como pendiente.')
    return redirect('administracion_laboratorios')