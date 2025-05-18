from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from inventario_nuevo.models import HistorialInventario
# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

@login_required
@admin_required #Verifica si el usuario es administrador
def tabla_historial_inventario(request):
    historial = HistorialInventario.objects.select_related(
        'producto', 'categoria', 'subcategoria', 'unidad_medida',
        'ubicacion_inicial', 'estado_inicial', 'agregado_por'
    ).order_by('-fecha_agregado')

    return render(request, 'inventario_nuevo/tabla_historial_inventario.html', {
        'historial': historial
    })
