from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import  SolicitudLaboratorio
from django.contrib.auth.models import User  # Importa el modelo de usuario de Django
from django.contrib import messages

from django.utils import timezone

#solicitar reservacion desde usuario sin privilegios de administrador
def reservar_laboratorio(request):
    if request.method == 'POST':
        laboratorio = request.POST['laboratorio']
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']

        # Validar que la hora de inicio sea anterior a la hora de fin
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser anterior a la hora de fin.")
            return redirect('reservar_laboratorio')

        # Crear la solicitud de reservación
        solicitud = SolicitudLaboratorio(
            usuario=request.user,
            laboratorio=laboratorio,
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=SolicitudLaboratorio.PENDIENTE
        )
        solicitud.save()

        messages.success(request, "La solicitud de reserva se ha creado exitosamente.")
        return redirect('reservar_laboratorio')

    # Obtener las solicitudes del usuario
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    return render(request, 'reservar_laboratorio.html', {'solicitudes': solicitudes})

def lista_solicitudes_usuario(request):
    # Filtra las solicitudes del usuario que está autenticado
    solicitudes = SolicitudLaboratorio.objects.filter(usuario=request.user)

    return render(request, 'appGestionLaboratorios/lista_solicitudes_usuario.html', {'solicitudes': solicitudes})

#views solo para opciones de administrador
# Vista para administrar las solicitudes de laboratorio
def administracionLaboratorios(request):
    # Obtén todas las solicitudes de laboratorio
    solicitudes = SolicitudLaboratorio.objects.all()  # O filtra según necesites
    return render(request, 'administracionLaboratorios.html', {'solicitudes': solicitudes})

# Vista para aprobar solicitudes
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    solicitud.estado = 'aprobada'
    solicitud.save()
    return redirect('administracion_laboratorios')  # Redirige a la lista de solicitudes

# Vista para rechazar solicitudes
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    solicitud.estado = 'rechazada'
    solicitud.save()
    return redirect('administracion_laboratorios')  # Redirige a la lista de solicitudes

# Vista para solicitudes en pendientes
def solicitud_pendiente(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudLaboratorio, id=solicitud_id)
    solicitud.estado = 'pendiente'
    solicitud.save()
    return redirect('administracion_laboratorios')  # Redirige a la lista de solicitudes