from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import UsoItemLaboratorio
from django.contrib import messages  # Importa para mostrar mensajes en la interfaz
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades

@login_required
def editar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    
    if uso_item.solicitud.estado != 'pendiente':
        messages.error(request, "Solo se pueden editar solicitudes pendientes.")
        return redirect('solicitar_recursos')
    
    if request.method == 'POST':
        cantidad_utilizada = request.POST.get('cantidad_utilizada')
        unidad_medida = request.POST.get('unidad_medida')
        
        try:
            cantidad_utilizada_decimal = Decimal(cantidad_utilizada)
            if cantidad_utilizada_decimal <= 0:
                messages.error(request, "La cantidad debe ser mayor a 0.")
                return redirect('editar_recurso', uso_id=uso_item.id)
        except (InvalidOperation, TypeError):
            messages.error(request, "Cantidad ingresada no válida.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        try:
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, uso_item.inventario.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {uso_item.inventario.unidad_medida}.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        if cantidad_convertida > uso_item.inventario.cantidad_disponible:
            messages.error(request, "Cantidad solicitada mayor a la existente en inventario.")
            return redirect('editar_recurso', uso_id=uso_item.id)
        
        uso_item.cantidad_utilizada = cantidad_utilizada_decimal
        uso_item.unidad_medida = unidad_medida
        uso_item.save()
        messages.success(request, "Solicitud actualizada correctamente.")
        return redirect('solicitar_recursos')
    
    return render(request, 'editar_recurso.html', {'uso_item': uso_item})