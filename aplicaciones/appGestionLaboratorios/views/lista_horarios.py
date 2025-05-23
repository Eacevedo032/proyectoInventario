from django.shortcuts import render
from django.core.paginator import Paginator
from aplicaciones.appGestionLaboratorios.models import HorarioLaboratorio
from datetime import date, time, timedelta

def obtener_intervalos_disponibles(reservas, hora_inicio_dia, hora_fin_dia):
    """
    Calcula los intervalos disponibles entre las reservas existentes.
    """
    disponibles = []
    hora_actual = hora_inicio_dia

    for reserva in reservas.order_by('hora_inicio'):
        if hora_actual < reserva.hora_inicio:
            disponibles.append((hora_actual, reserva.hora_inicio))
        hora_actual = max(hora_actual, reserva.hora_fin)

    if hora_actual < hora_fin_dia:
        disponibles.append((hora_actual, hora_fin_dia))

    return disponibles

def listar_horarios_lectura(request):
    # Filtros
    fecha_seleccionada = request.GET.get('fecha', '')
    estado_seleccionado = request.GET.get('estado', '')
    laboratorio_seleccionado = request.GET.get('laboratorio', '')
    
    fecha_hoy = date.today()
    fechas = [fecha_hoy + timedelta(days=i) for i in range(7)]  # Próximos 7 días
    laboratorios = [
        "Laboratorio Planta Alta",
        "Laboratorio Planta Baja",
        "Laboratorio Bio-Microbiana"
    ]
    estados_disponibles = ['Disponible', 'Ocupado']

    resultados = {}

    for lab in laboratorios:
        # Si hay filtro de laboratorio y no es este, saltar
        if laboratorio_seleccionado and lab != laboratorio_seleccionado:
            continue
            
        resultados[lab] = []
        for fecha in fechas:
            # Si hay filtro de fecha y no es esta, saltar
            if fecha_seleccionada and str(fecha) != fecha_seleccionada:
                continue
                
            reservas = HorarioLaboratorio.objects.filter(
                laboratorio=lab,
                fecha_reserva=fecha
            ).order_by('hora_inicio')

            # Intervalos DISPONIBLES
            if not estado_seleccionado or estado_seleccionado == 'Disponible':
                disponibles = obtener_intervalos_disponibles(
                    reservas,
                    time(8, 0),  # Apertura del laboratorio
                    time(17, 0)  # Cierre del laboratorio
                )

                for inicio, fin in disponibles:
                    resultados[lab].append({
                        'fecha': fecha,
                        'inicio': inicio,
                        'fin': fin,
                        'estado': 'Disponible'
                    })

            # Intervalos OCUPADOS
            if not estado_seleccionado or estado_seleccionado == 'Ocupado':
                for r in reservas:
                    resultados[lab].append({
                        'fecha': fecha,
                        'inicio': r.hora_inicio,
                        'fin': r.hora_fin,
                        'estado': 'Ocupado'
                    })

        # Ordenar resultados por fecha y hora de inicio
        resultados[lab].sort(key=lambda x: (x['fecha'], x['inicio']))
        
        # Paginación por laboratorio
        paginator = Paginator(resultados[lab], 5)  # 5 items por página
        page_number = request.GET.get(f'page_{lab}', 1)
        page_obj = paginator.get_page(page_number)
        resultados[lab] = page_obj

    context = {
        'resultados': resultados,
        'fechas_disponibles': fechas,
        'laboratorios': laboratorios,
        'estados': estados_disponibles,
        'filtros': {
            'fecha': fecha_seleccionada,
            'estado': estado_seleccionado,
            'laboratorio': laboratorio_seleccionado
        }
    }
    return render(request, 'listar_horarios_lectura.html', context)
