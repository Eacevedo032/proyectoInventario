from django.shortcuts import render
from django.contrib.auth.decorators import login_required

#Menu principal de Inicio del Inventario.
@login_required
def menu_catalogos(request):
    return render(request, 'inventario_nuevo/menu_catalogos.html')

#Menu principal de Inicio del Inventario.
@login_required
def menu_inventario(request):
    return render(request, 'inventario_nuevo/menu_inventario.html')

