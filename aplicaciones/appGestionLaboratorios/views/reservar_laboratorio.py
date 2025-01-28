from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import SolicitudLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz

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
                for error in error_list:
                    messages.error(request, error)
            return redirect('reservar_laboratorio')

        solicitud.save()
        messages.success(request, 'La solicitud de reserva se ha creado exitosamente.')
        return redirect('reservar_laboratorio')

    # Obtener todas las solicitudes del usuario autenticado, ordenadas de la más reciente a la más antigua
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user).order_by('-fecha_reserva', '-hora_inicio')

    return render(request, 'reservar_laboratorio.html', {'solicitudes': solicitudes})

# Eliminar solicitud de laboratorio
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'La solicitud ha sido eliminada exitosamente.')
        return redirect('reservar_laboratorio')
    return render(request, 'reservar_laboratorio.html', {'solicitud': solicitud})


#eliminar solicitud de laboratorio
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'La solicitud ha sido eliminada exitosamente.')
        return redirect('reservar_laboratorio')  
    return render(request, 'reservar_laboratorio.html', {'solicitud': solicitud})