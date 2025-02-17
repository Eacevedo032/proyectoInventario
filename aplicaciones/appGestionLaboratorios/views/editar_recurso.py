from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import UsoItemLaboratorio
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades

def es_admin(user):
    """Función para verificar si el usuario es staff o superuser."""
    return user.is_staff or user.is_superuser

@login_required
def editar_recurso(request, uso_id):
    print("Entrando en la vista editar_recurso...")  # Verificamos si entra a la vista

    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    print(f"Uso ID recibido: {uso_id}")  # Verificamos que el ID sea correcto

    # Verificar que la solicitud esté en estado pendiente
    if uso_item.solicitud.estado != 'pendiente':
        messages.error(request, "Solo se pueden editar solicitudes pendientes.")
        return redirect('solicitar_recursos')

    if request.method == 'POST':
        cantidad_utilizada = request.POST.get('cantidad_utilizada')
        unidad_medida = request.POST.get('unidad_medida')

        # Validación de cantidad
        try:
            cantidad_utilizada_decimal = Decimal(cantidad_utilizada)
            if cantidad_utilizada_decimal <= 0:
                messages.error(request, "La cantidad debe ser mayor a 0.")
                return redirect('editar_recurso', uso_id=uso_item.id)
        except (InvalidOperation, TypeError):
            messages.error(request, "Cantidad ingresada no válida.")
            return redirect('editar_recurso', uso_id=uso_item.id)

        # Conversión de unidades
        try:
            cantidad_convertida = convertir_unidades(cantidad_utilizada_decimal, unidad_medida, uso_item.inventario.unidad_medida)
        except ValueError:
            messages.error(request, f"No se pueden convertir {unidad_medida} a {uso_item.inventario.unidad_medida}.")
            return redirect('editar_recurso', uso_id=uso_item.id)

        # Verificación de cantidad en inventario
        if cantidad_convertida > uso_item.inventario.cantidad_disponible:
            messages.error(request, "Cantidad solicitada mayor a la existente en inventario.")
            return redirect('editar_recurso', uso_id=uso_item.id)

        # Actualización del recurso
        uso_item.cantidad_utilizada = cantidad_utilizada_decimal
        uso_item.unidad_medida = unidad_medida
        uso_item.save()
        messages.success(request, "Solicitud actualizada correctamente.")
        # Redirigir según el tipo de usuario
        if es_admin(request.user):
            print("Usuario es staff o superuser, redirigiendo a ver_items_solicitud")
            return redirect('ver_items_solicitud', solicitud_id=uso_item.solicitud.id)
        else:
            print("Usuario es normal, redirigiendo a solicitar_recursos")
            return redirect('solicitar_recursos')

    return render(request, 'editar_recurso.html', {'uso_item': uso_item})


#eliminar recursos solicitados
@login_required
def eliminar_recurso(request, uso_id):
    uso_item = get_object_or_404(UsoItemLaboratorio, id=uso_id)
    
    # Solo se pueden eliminar ítems de solicitudes en estado 'pendiente'
    if uso_item.solicitud.estado != 'pendiente':
        messages.error(request, "Solo se pueden eliminar ítems de solicitudes pendientes.")
        return redirect('solicitar_recursos')  # Redirige si la solicitud no está pendiente

    # Eliminar el ítem
    uso_item.delete()
    messages.success(request, "Ítem eliminado correctamente.")
    return redirect('ver_items_solicitud', solicitud_id=uso_item.solicitud.id)  # Redirige a la vista de ver ítems solicitados