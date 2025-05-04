from django.shortcuts import render, redirect
from inventario_nuevo.models import TransferenciaProducto, Producto
from inventario_nuevo.models import InventarioDiario
from aplicaciones.appGestionLaboratorios.views.convertir_unidades import convertir_usando_modelo
from decimal import Decimal
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
import pandas as pd

# REGISTRAR INVENTARIO FÍSICO
def registrar_inventario(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha', None)

        # Si no se envió fecha, usar la fecha actual
        if not fecha:
            fecha = timezone.now().strftime("%Y-%m-%d")

        productos = Producto.objects.all()

        for producto in productos:
            cantidad_final = request.POST.get(f'cantidad_{producto.id}')
            
            if cantidad_final:
                cantidad_final = int(cantidad_final)
                
                # Actualizar el producto
                producto.cantidad_disponible = cantidad_final  
                producto.save()  

                # Guardar/Actualizar InventarioDiario
                inventario, created = InventarioDiario.objects.get_or_create(producto=producto, fecha=fecha)
                inventario.cantidad_final = cantidad_final
                
                if created:
                    inventario.cantidad_inicial = cantidad_final  # Si es nuevo, inicia con la cantidad final
                
                # Asignar el usuario autenticado
                inventario.usuario = request.user  

                inventario.calcular_diferencia()
                inventario.save()

        messages.success(request, "Inventario actualizado correctamente.")
        return redirect(reverse('reporte_inventario_diario', kwargs={'fecha': fecha}))

    productos = Producto.objects.all()
    return render(request, 'inventario_nuevo/registrar_inventario.html', {'productos': productos})
    
# REPORTE GENERAL DE INVENTARIO
def reporte_inventario_diario(request, fecha):
    movimientos = InventarioDiario.objects.filter(fecha=fecha).order_by('producto')

    print(f"Movimientos encontrados para {fecha}: {movimientos.count()}")

    return render(request, 'inventario_nuevo/reporte_inventario_diario.html', {'movimientos': movimientos, 'fecha': fecha})

def seleccion_reportes(request):
    return render(request, 'inventario_nuevo/seleccion_reportes.html')

def reporte_inventario(request):
    movimientos = InventarioDiario.objects.all().order_by('-fecha')
    return render(request, 'inventario_nuevo/reporte_inventario.html', {'movimientos': movimientos})

#TRANSFERENCIA REGISTRA Y ACTUALIZA
def transferencia_producto(request):
    productos = Producto.objects.all()
    estados = ["Dado de baja", "Mantenimiento", "No Disponible", "Prestado", "Ingreso"]

    if request.method == 'POST':
        producto = Producto.objects.get(id=request.POST.get('producto_id'))
        estado_destino = request.POST.get('estado')
        cantidad_transferida = Decimal(request.POST.get('cantidad', 0))  #Convierte a Decimal
        usuario = request.user  #Captura el usuario autenticado
        motivo = request.POST.get('motivo', '')

        #Ajuste automático del inventario
        inventario, created = InventarioDiario.objects.get_or_create(producto=producto, fecha=timezone.now().date())

        if estado_destino == "Ingreso":
            inventario.cantidad_final += cantidad_transferida  #Aumenta cantidad
        else:
            inventario.cantidad_final -= cantidad_transferida  #Reduce cantidad
        
        inventario.calcular_diferencia()  #Calcula la diferencia correctamente
        inventario.save()

        #egistrar la transferencia en el historial
        TransferenciaProducto.objects.create(
            producto=producto,
            usuario=usuario, 
            estado_destino=estado_destino,
            cantidad=cantidad_transferida,
            motivo=motivo,
            fecha_transferencia=timezone.now().date()
        )

        return redirect(reverse('historial_transferencias'))  #Redirige al historial

    return render(request, 'inventario_nuevo/transferencia_producto.html', {'productos': productos, 'estados': estados})

def historial_transferencias(request):
    transferencias = TransferenciaProducto.objects.all().order_by('-fecha_transferencia')
    return render(request, 'inventario_nuevo/historial_transferencias.html', {'transferencias': transferencias})

# REPORTE DE INVENTARIO DIARIO
def reporte_inventario_diario(request):
    fecha_str = request.GET.get('fecha')  #Obtener fecha de la solicitud
    try:
        fecha = timezone.datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else timezone.now().date()
    except ValueError:
        fecha = timezone.now().date()  #Si la fecha no es válida, usa la actual

    movimientos = InventarioDiario.objects.filter(fecha=fecha).order_by('producto')
    transferencias = TransferenciaProducto.objects.filter(fecha_transferencia=fecha).order_by('-fecha_transferencia')

    print(f"Movimientos encontrados para {fecha}: {movimientos.count()}")  # Debugging en la terminal
    print(f"Transferencias encontradas para {fecha}: {transferencias.count()}")  # Debugging en la terminal

    return render(request, 'inventario_nuevo/reporte_inventario_diario.html', {
        'movimientos': movimientos, 
        'transferencias': transferencias, 
        'fecha': fecha
    })

# PDFfrom django.http import HttpResponse
def exportar_pdf(request):
    #Cargar la plantilla HTML del reporte de inventario
    template = get_template("inventario_nuevo/reporte_inventario.html")  
    context = {
        "movimientos": InventarioDiario.objects.all().order_by("-fecha"),
    }
    
    #Renderizar el HTML con los datos actuales
    html_content = template.render(context)

    #Configurar la respuesta para descargar el PDF automáticamente
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Reporte_Inventario.pdf"'

    #Aplicar estilos CSS para mejorar la estructura del cuadro y ajustar la página
    css = CSS(string="""
        @page { size: A4 landscape; margin: 20mm; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
    """)

    #Generar el PDF con formato optimizado
    pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])
    response.write(pdf_bytes)

    return response

# EXCEL
def exportar_excel(request):
    movimientos = InventarioDiario.objects.all().values('fecha', 'producto__nombre', 'usuario__username', 'cantidad_inicial', 'cantidad_final', 'diferencia')  # Corrección aquí

    df = pd.DataFrame(list(movimientos))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.xlsx"'
    
    df.to_excel(response, index=False)
    return response
