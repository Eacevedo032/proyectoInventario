from decimal import Decimal
from django.forms import ValidationError
from django.utils import timezone
from itertools import groupby
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import Categoria, HistorialInventario, Inventario, SolicitudLaboratorio, HorarioLaboratorio, SubCategoria, UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.db import transaction
from django.db.models import Q
from datetime import date
from django.utils.dateparse import parse_date

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

        try:
            # Validar que la solicitud no se superponga con otra solicitud
            solicitud.full_clean()
        except ValidationError as e:
            for field, error_list in e.message_dict.items():
             for error in error_list: messages.error(request, error)
            return redirect('reservar_laboratorio')
        
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

#ver horarios que ya estan ocupados en los laboratorios
def listar_horarios_lectura(request):
    # Obtener todos los horarios desde la fecha actual
    horarios = HorarioLaboratorio.objects.filter(
        fecha_reserva__gte=date.today()
    ).order_by('fecha_reserva', 'hora_inicio')

    # Dividir horarios ocupados y bloqueados basándonos en el campo 'sin_supervision'
    laboratorio1_ocupados = horarios.filter(laboratorio="Laboratorio Planta Alta", sin_supervision=False)
    laboratorio2_ocupados = horarios.filter(laboratorio="Laboratorio Planta Baja", sin_supervision=False)
    laboratorio3_ocupados = horarios.filter(laboratorio="Laboratorio Microbial", sin_supervision=False)

    laboratorio1_bloqueados = horarios.filter(laboratorio="Laboratorio Planta Alta", sin_supervision=True)
    laboratorio2_bloqueados = horarios.filter(laboratorio="Laboratorio Planta Baja", sin_supervision=True)
    laboratorio3_bloqueados = horarios.filter(laboratorio="Laboratorio Microbial", sin_supervision=True)

    return render(request, 'listar_horarios_lectura.html', {
        'laboratorio1_ocupados': laboratorio1_ocupados,
        'laboratorio2_ocupados': laboratorio2_ocupados,
        'laboratorio3_ocupados': laboratorio3_ocupados,
        'laboratorio1_bloqueados': laboratorio1_bloqueados,
        'laboratorio2_bloqueados': laboratorio2_bloqueados,
        'laboratorio3_bloqueados': laboratorio3_bloqueados,
    })

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
    if solicitud.estado == 'aprobada':
        messages.error(request, 'Esta solicitud ya fue aprobada.')
        return redirect('administracion_laboratorios')

    try:
        solicitud.full_clean()
    except ValidationError as e:
        for field, error_list in e.message_dict.items():
            for error in error_list:
                messages.error(request, error)
                solicitud.estado = 'rechazada'
        solicitud.save()
        return redirect('administracion_laboratorios')

    # Verificamos si el laboratorio está disponible
    conflictos = HorarioLaboratorio.objects.filter(
        laboratorio=solicitud.laboratorio,
        fecha_reserva=solicitud.fecha_reserva,
        hora_inicio__lt=solicitud.hora_fin,
        hora_fin__gt=solicitud.hora_inicio,
    )

    if conflictos.exists():
        messages.error(request, 'El laboratorio ya está reservado en el horario solicitado.')
        return redirect('administracion_laboratorios')

    # Si no hay conflictos, procedemos a aprobar la solicitud.
    solicitud.estado = 'aprobada'

    with transaction.atomic():
        items_solicitados = UsoItemLaboratorio.objects.filter(solicitud=solicitud)

        for item in items_solicitados:
            inventario_item = item.inventario  # Cambiado a 'inventario'

            if Decimal(inventario_item.cantidad_disponible) >= Decimal(item.cantidad_utilizada):
                inventario_item.cantidad_disponible = Decimal(inventario_item.cantidad_disponible) - Decimal(item.cantidad_utilizada) 
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

        # Registrar horario de ocupación
        HorarioLaboratorio.objects.create(
            laboratorio=solicitud.laboratorio,
            fecha_reserva=solicitud.fecha_reserva,
            hora_inicio=solicitud.hora_inicio,
            hora_fin=solicitud.hora_fin,
        )

        solicitud.save()
        messages.success(request, 'La solicitud ha sido aprobada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para rechazar solicitudes
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede rechazar una solicitud aprobada.')
        return redirect('administracion_laboratorios')
    
    solicitud.estado = 'rechazada'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido rechazada exitosamente.')
    return redirect('administracion_laboratorios')

# Vista para solicitudes pendientes
def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    
    if solicitud.estado == 'aprobada':
        messages.error(request, 'No se puede marcar como pendiente una solicitud aprobada.')
        return redirect('administracion_laboratorios')
    
    solicitud.estado = 'pendiente'
    solicitud.save()
    messages.success(request, 'La solicitud ha sido marcada como pendiente.')
    return redirect('administracion_laboratorios')

#configuraciones para el horario de laboratorios desde admin
@login_required
def agregar_horario(request):
    if request.method == 'POST':
        laboratorio = request.POST.get('laboratorio')
        fecha_reserva = request.POST.get('fecha_reserva')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        sin_supervision = request.POST.get('sin_supervision') == 'on'

        if hora_inicio >= hora_fin:
            return render(request, 'agregar_horario.html', {
                'error': 'La hora de inicio debe ser anterior a la hora de fin.',
                'laboratorio': laboratorio,
                'fecha_reserva': fecha_reserva,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'sin_supervision': sin_supervision,
            })

        if sin_supervision:
            # Bloqueo para todos los laboratorios
            for lab in ["Laboratorio Planta Alta", "Laboratorio Planta Baja", "Laboratorio Microbial"]:
                HorarioLaboratorio.objects.create(
                    laboratorio=lab,
                    fecha_reserva=fecha_reserva,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    sin_supervision=True,
                )
        else:
            # Crear horario normal
            HorarioLaboratorio.objects.create(
                laboratorio=laboratorio,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                sin_supervision=False,
            )
        return redirect('listar_horarios')

    return render(request, 'agregar_horario.html')

#listar horario
def listar_horarios(request):
    horarios = HorarioLaboratorio.objects.filter(
        Q(fecha_reserva__gte=date.today())
    ).order_by('fecha_reserva', 'hora_inicio')

    laboratorio1 = horarios.filter(laboratorio="Laboratorio Planta Alta")
    laboratorio2 = horarios.filter(laboratorio="Laboratorio Planta Baja")
    laboratorio3 = horarios.filter(laboratorio="Laboratorio Microbial")
    bloqueos = horarios.filter(sin_supervision=True)  # Bloqueos sin supervisión

    return render(request, 'listar_horarios.html', {
        'laboratorio1': laboratorio1,
        'laboratorio2': laboratorio2,
        'laboratorio3': laboratorio3,
        'bloqueos': bloqueos,  # Enviar bloqueos al template
    })

#Eliminar horario
def eliminar_horario(request, horario_id):
    horario = get_object_or_404(HorarioLaboratorio, id=horario_id)
    horario.delete()
    return redirect('listar_horarios')

#Editar horario
def editar_horario(request, horario_id):
    # Buscar el horario a editar
    horario = get_object_or_404(HorarioLaboratorio, id=horario_id)

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            laboratorio = request.POST.get('laboratorio')
            fecha_reserva = parse_date(request.POST.get('fecha_reserva'))
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            sin_supervision = request.POST.get('sin_supervision') == 'on'

            # Validaciones adicionales
            if hora_inicio >= hora_fin:
                messages.error(request, 'La hora de inicio debe ser anterior a la hora de fin.')
                return render(request, 'editar_horario.html', {'horario': horario})

            # Actualizar los datos del horario
            horario.laboratorio = laboratorio
            horario.fecha_reserva = fecha_reserva
            horario.hora_inicio = hora_inicio
            horario.hora_fin = hora_fin
            horario.sin_supervision = sin_supervision
            horario.save()

            # Mensaje de éxito y redirección
            messages.success(request, 'Horario actualizado correctamente.')
            return redirect('listar_horarios')

        except Exception as e:
            # Manejar errores inesperados
            messages.error(request, f'Ocurrió un error al guardar: {str(e)}')
            return render(request, 'editar_horario.html', {'horario': horario})

    # Formatear fecha para la plantilla
    horario.fecha_reserva = horario.fecha_reserva.strftime('%Y-%m-%d') if horario.fecha_reserva else ''
    return render(request, 'editar_horario.html', {'horario': horario})
