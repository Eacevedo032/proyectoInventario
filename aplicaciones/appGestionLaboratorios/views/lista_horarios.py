from django.shortcuts import render
from aplicaciones.appGestionInventario.models import HorarioLaboratorio
from datetime import date

#ver horarios que ya estan ocupados en los laboratorios por usuario sin provilegios
def listar_horarios_lectura(request):
    # Obtener todos los horarios desde la fecha actual
    horarios = HorarioLaboratorio.objects.filter(
        fecha_reserva__gte=date.today()
    ).order_by('fecha_reserva', 'hora_inicio')

    # Dividir horarios ocupados y bloqueados basándonos en el campo 'sin_supervision'
    laboratorio1_ocupados = horarios.filter(laboratorio="Laboratorio Planta Alta", sin_supervision=False)
    laboratorio2_ocupados = horarios.filter(laboratorio="Laboratorio Planta Baja", sin_supervision=False)
    laboratorio3_ocupados = horarios.filter(laboratorio="Laboratorio Microbiana", sin_supervision=False)

    laboratorio1_bloqueados = horarios.filter(laboratorio="Laboratorio Planta Alta", sin_supervision=True)
    laboratorio2_bloqueados = horarios.filter(laboratorio="Laboratorio Planta Baja", sin_supervision=True)
    laboratorio3_bloqueados = horarios.filter(laboratorio="Laboratorio Microbiana", sin_supervision=True)

    return render(request, 'listar_horarios_lectura.html', {
        'laboratorio1_ocupados': laboratorio1_ocupados,
        'laboratorio2_ocupados': laboratorio2_ocupados,
        'laboratorio3_ocupados': laboratorio3_ocupados,
        'laboratorio1_bloqueados': laboratorio1_bloqueados,
        'laboratorio2_bloqueados': laboratorio2_bloqueados,
        'laboratorio3_bloqueados': laboratorio3_bloqueados,
    })