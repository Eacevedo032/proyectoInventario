from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionLaboratorios.models import HorarioLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from datetime import date
from django.utils.dateparse import parse_date
from django.db.models import Q

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#configuraciones para el horario de laboratorios desde admin
@login_required
@admin_required #Verifica si el usuario es administrador
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
            for lab in ["Laboratorio Planta Alta", "Laboratorio Planta Baja", "Laboratorio Microbiana"]:
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
@admin_required #Verifica si el usuario es administrador
def listar_horarios(request):
    horarios = HorarioLaboratorio.objects.filter(
        Q(fecha_reserva__gte=date.today())
    ).order_by('fecha_reserva', 'hora_inicio')

    laboratorio1 = horarios.filter(laboratorio="Laboratorio Planta Alta")
    laboratorio2 = horarios.filter(laboratorio="Laboratorio Planta Baja")
    laboratorio3 = horarios.filter(laboratorio="Laboratorio Microbiana")
    bloqueos = horarios.filter(sin_supervision=True)  # Bloqueos sin supervisión

    return render(request, 'listar_horarios.html', {
        'laboratorio1': laboratorio1,
        'laboratorio2': laboratorio2,
        'laboratorio3': laboratorio3,
        'bloqueos': bloqueos,  # Enviar bloqueos al template
    })

#Eliminar horario
@login_required
@admin_required #Verifica si el usuario es administrador
def eliminar_horario(request, horario_id):
    horario = get_object_or_404(HorarioLaboratorio, id=horario_id)
    horario.delete()
    return redirect('listar_horarios')

#Editar horario
@admin_required #Verifica si el usuario es administrador
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