from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from aplicaciones.appGestionInventario.models import HistorialInventario, Inventario
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_unidades

@login_required
def registrar_cambio_inventario(request):
    inventarios = Inventario.objects.all()
    historial = HistorialInventario.objects.all().order_by('-fecha_cambio')
    usuarios = User.objects.all()

    # Filtros
    producto_id = request.GET.get('producto')
    tipo_cambio = request.GET.get('tipo_cambio')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario_id = request.GET.get('usuario')

    if producto_id:
        historial = historial.filter(inventario__id_inventario=producto_id)
    if tipo_cambio:
        historial = historial.filter(tipo_cambio=tipo_cambio)
    if fecha_inicio and fecha_fin:
        historial = historial.filter(fecha_cambio__range=[fecha_inicio, fecha_fin])
    if usuario_id:
        historial = historial.filter(modificado_por_id=usuario_id)

    if request.method == "POST":
        inventario_id = request.POST.get("inventario")
        cantidad_cambiada = Decimal(request.POST.get("cantidad_cambiada"))
        unidad_medida = request.POST.get("unidad_medida")
        tipo_cambio = request.POST.get("tipo_cambio")
        descripcion = request.POST.get("descripcion")

        if not inventario_id:
            messages.error(request, "Por favor, selecciona un producto del inventario.")
            return redirect("registrar_cambio_inventario")

        inventario_item = get_object_or_404(Inventario, id_inventario=inventario_id)
        cantidad_anterior = inventario_item.cantidad_disponible

        # Verifica la unidad de medida base del inventario
        unidad_base = inventario_item.unidad_medida  

        # Si la unidad ingresada y la unidad base son "unidades", no es necesario convertir
        if unidad_medida == "unidades" and unidad_base == "unidades":
            cantidad_convertida = cantidad_cambiada  # Mantiene la misma cantidad sin conversión, la asigno para las conversiones
        else:
            try:
                print(f"Unidad ingresada: {unidad_medida}, Unidad base en inventario: {unidad_base}")
                print(f"Intentando convertir {cantidad_cambiada} de {unidad_medida} a {unidad_base}")
        
                cantidad_convertida = convertir_unidades(cantidad_cambiada, unidad_medida, unidad_base)
            except ValueError as e:
                messages.error(request, f"Error en la conversión de unidades: {str(e)}")
                return redirect("registrar_cambio_inventario")

        with transaction.atomic():
            if tipo_cambio == "entrada":
                inventario_item.cantidad_disponible += cantidad_convertida  # cantidad_convertida para operaciones de conversión
            elif tipo_cambio == "salida":
                if inventario_item.cantidad_disponible >= cantidad_convertida:  
                    inventario_item.cantidad_disponible -= cantidad_convertida  
                else:
                    messages.error(request, f"No hay suficiente cantidad de {inventario_item.nombre} en inventario.")
                    return redirect("registrar_cambio_inventario")

            inventario_item.save()
            HistorialInventario.objects.create(
                inventario=inventario_item,
                cantidad_anterior=cantidad_anterior,
                cantidad_cambiada=cantidad_convertida,  # Guarda la cantidad ya convertida
                unidad_medida=unidad_base,  # Guarda en la unidad base
                fecha_cambio=timezone.now().date(),
                tipo_cambio=tipo_cambio,
                modificado_por=request.user,
                descripcion=descripcion
            )

        messages.success(request, "El cambio de inventario se ha registrado exitosamente.")
        return redirect("registrar_cambio_inventario")

    return render(request, 'registrar_cambio_inventario.html', {
        'inventarios': inventarios,
        'historial': historial,
        'usuarios': usuarios,
    })