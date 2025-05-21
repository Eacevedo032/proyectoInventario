from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from aplicaciones.appGestionLaboratorios.models import HorarioLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from datetime import date, datetime
from django.utils.dateparse import parse_date, parse_time
from django.db.models import Q

# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#configuraciones para el horario de laboratorios desde admin
@login_required
@admin_required
def agregar_horario(request):
    if request.method == 'POST':
        laboratorio = request.POST.get('laboratorio')
        fecha_reserva = request.POST.get('fecha_reserva')
        sin_supervision = request.POST.get('sin_supervision') == 'on'
        
        try:
            # Convertir horas a formato 24h
            hora_inicio_num = int(request.POST.get('hora_inicio'))
            minuto_inicio = request.POST.get('minuto_inicio')
            periodo_inicio = request.POST.get('periodo_inicio')
            
            if periodo_inicio == 'PM' and hora_inicio_num != 12:
                hora_inicio_num += 12
            elif periodo_inicio == 'AM' and hora_inicio_num == 12:
                hora_inicio_num = 0
            hora_inicio = f"{hora_inicio_num:02d}:{minuto_inicio}:00"

            hora_fin_num = int(request.POST.get('hora_fin'))
            minuto_fin = request.POST.get('minuto_fin')
            periodo_fin = request.POST.get('periodo_fin')
            
            if periodo_fin == 'PM' and hora_fin_num != 12:
                hora_fin_num += 12
            elif periodo_fin == 'AM' and hora_fin_num == 12:
                hora_fin_num = 0
            hora_fin = f"{hora_fin_num:02d}:{minuto_fin}:00"

            # Validar que el horario no exista ya
            existe_horario = HorarioLaboratorio.objects.filter(
                laboratorio=laboratorio,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            ).exists()

            if existe_horario:
                messages.error(request, 'Ya existe un horario con estos mismos datos.')
                return render(request, 'agregar_horario.html', {
                    'laboratorio': laboratorio,
                    'fecha_reserva': fecha_reserva,
                    'sin_supervision': sin_supervision,
                })

            if hora_inicio >= hora_fin:
                messages.error(request, 'La hora de inicio debe ser anterior a la hora de fin.')
                return render(request, 'agregar_horario.html', {
                    'laboratorio': laboratorio,
                    'fecha_reserva': fecha_reserva,
                    'sin_supervision': sin_supervision,
                })

            if sin_supervision:
                # Para bloqueos, verificar que no haya horarios existentes que se solapen
                horarios_existentes = HorarioLaboratorio.objects.filter(
                    laboratorio=laboratorio,
                    fecha_reserva=fecha_reserva,
                ).exclude(
                    hora_fin__lte=hora_inicio
                ).exclude(
                    hora_inicio__gte=hora_fin
                ).exists()

                if horarios_existentes:
                    messages.error(request, 'Existen horarios que se solapan con este bloqueo.')
                    return render(request, 'agregar_horario.html', {
                        'laboratorio': laboratorio,
                        'fecha_reserva': fecha_reserva,
                        'sin_supervision': sin_supervision,
                    })

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
                # Para horarios normales, verificar solapamiento
                horarios_existentes = HorarioLaboratorio.objects.filter(
                    laboratorio=laboratorio,
                    fecha_reserva=fecha_reserva,
                    sin_supervision=False
                ).exclude(
                    hora_fin__lte=hora_inicio
                ).exclude(
                    hora_inicio__gte=hora_fin
                ).exists()

                if horarios_existentes:
                    messages.error(request, 'Ya existe un horario que se solapa con este.')
                    return render(request, 'agregar_horario.html', {
                        'laboratorio': laboratorio,
                        'fecha_reserva': fecha_reserva,
                        'sin_supervision': sin_supervision,
                    })

                HorarioLaboratorio.objects.create(
                    laboratorio=laboratorio,
                    fecha_reserva=fecha_reserva,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    sin_supervision=False,
                )

            messages.success(request, 'Horario agregado correctamente.')
            return redirect('listar_horarios')

        except (ValueError, TypeError) as e:
            messages.error(request, f'Error en los datos ingresados: {str(e)}')
            return render(request, 'agregar_horario.html', {
                'laboratorio': laboratorio,
                'fecha_reserva': fecha_reserva,
                'sin_supervision': sin_supervision,
            })

    return render(request, 'agregar_horario.html')

#listar horario
@admin_required
@login_required
def listar_horarios(request):
    horarios = HorarioLaboratorio.objects.filter(
        Q(fecha_reserva__gte=date.today())
    ).order_by('fecha_reserva', 'hora_inicio')

    laboratorio1 = horarios.filter(laboratorio="Laboratorio Planta Alta")
    laboratorio2 = horarios.filter(laboratorio="Laboratorio Planta Baja")
    laboratorio3 = horarios.filter(laboratorio="Laboratorio Microbiana")
    bloqueos = horarios.filter(sin_supervision=True)

    # Paginación por laboratorio y bloqueos
    paginador1 = Paginator(laboratorio1, 10)
    paginador2 = Paginator(laboratorio2, 10)
    paginador3 = Paginator(laboratorio3, 10)
    paginador_bloqueos = Paginator(bloqueos, 10)

    # Obtener página actual desde el parámetro GET
    page1 = request.GET.get('page1')
    page2 = request.GET.get('page2')
    page3 = request.GET.get('page3')
    page_bloqueos = request.GET.get('page_bloqueos')

    return render(request, 'listar_horarios.html', {
        'laboratorio1': paginador1.get_page(page1),
        'laboratorio2': paginador2.get_page(page2),
        'laboratorio3': paginador3.get_page(page3),
        'bloqueos': paginador_bloqueos.get_page(page_bloqueos),
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
@login_required
def editar_horario(request, horario_id):
    # Buscar el horario a editar
    horario = get_object_or_404(HorarioLaboratorio, id=horario_id)

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            laboratorio = request.POST.get('laboratorio')
            fecha_reserva = parse_date(request.POST.get('fecha_reserva'))
            sin_supervision = request.POST.get('sin_supervision') == 'on'
            
            # Obtener valores de hora del formulario
            hora_inicio_num = int(request.POST.get('hora_inicio'))
            minuto_inicio = request.POST.get('minuto_inicio')
            periodo_inicio = request.POST.get('periodo_inicio')
            
            # Convertir a formato 24 horas
            if periodo_inicio == 'PM' and hora_inicio_num != 12:
                hora_inicio_num += 12
            elif periodo_inicio == 'AM' and hora_inicio_num == 12:
                hora_inicio_num = 0
            hora_inicio = f"{hora_inicio_num:02d}:{minuto_inicio}"

            # Hora de fin
            hora_fin_num = int(request.POST.get('hora_fin'))
            minuto_fin = request.POST.get('minuto_fin')
            periodo_fin = request.POST.get('periodo_fin')
            
            if periodo_fin == 'PM' and hora_fin_num != 12:
                hora_fin_num += 12
            elif periodo_fin == 'AM' and hora_fin_num == 12:
                hora_fin_num = 0
            hora_fin = f"{hora_fin_num:02d}:{minuto_fin}"

            # Validaciones
            if hora_inicio >= hora_fin:
                messages.error(request, 'La hora de inicio debe ser anterior a la hora de fin.')
                return render(request, 'editar_horario.html', get_horario_context(horario))

            # Actualizar horario
            horario.laboratorio = laboratorio
            horario.fecha_reserva = fecha_reserva
            horario.hora_inicio = hora_inicio
            horario.hora_fin = hora_fin
            horario.sin_supervision = sin_supervision
            horario.save()

            messages.success(request, 'Horario actualizado correctamente.')
            return redirect('listar_horarios')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al guardar: {str(e)}')
            return render(request, 'editar_horario.html', get_horario_context(horario))

    return render(request, 'editar_horario.html', get_horario_context(horario))

def get_horario_context(horario):
    """Función auxiliar para preparar el contexto con las horas convertidas"""
    # Convertir hora_inicio a formato 12h
    hora_inicio_24h = horario.hora_inicio
    if isinstance(hora_inicio_24h, str):
        hora_inicio_24h = parse_time(hora_inicio_24h)
    
    hora_inicio_12h = {
        'hora': hora_inicio_24h.hour % 12 or 12,
        'minuto': hora_inicio_24h.minute,
        'periodo': 'AM' if hora_inicio_24h.hour < 12 else 'PM'
    }
    
    # Convertir hora_fin a formato 12h
    hora_fin_24h = horario.hora_fin
    if isinstance(hora_fin_24h, str):
        hora_fin_24h = parse_time(hora_fin_24h)
    
    hora_fin_12h = {
        'hora': hora_fin_24h.hour % 12 or 12,
        'minuto': hora_fin_24h.minute,
        'periodo': 'AM' if hora_fin_24h.hour < 12 else 'PM'
    }
    
    return {
        'horario': horario,
        'fecha_reserva': horario.fecha_reserva.strftime('%Y-%m-%d') if horario.fecha_reserva else '',
        'hora_inicio_12h': hora_inicio_12h,
        'hora_fin_12h': hora_fin_12h,
    }