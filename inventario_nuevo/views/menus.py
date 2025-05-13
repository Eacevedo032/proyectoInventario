from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Decorador para verificar si el usuario es administrador
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

#Menu principal de Inicio del Inventario.
@admin_required #Verifica si el usuario es administrador
@login_required
def menu_catalogos(request):
    return render(request, 'inventario_nuevo/menu_catalogos.html')
