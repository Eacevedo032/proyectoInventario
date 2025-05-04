from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from .categorias import *
from .subcategorias import *
from .inventario import *
from .Usuarios import *
from .registrar_cambio_inventario import *

@cache_control(no_cache=True, must_revalidate=True, no_store=True) #controla la cache. En otras palabras, siempre 
#deben hacer una nueva solicitud al servidor para obtener la versión más reciente.
def SISLAB(request):
    if request.user.is_authenticated:
        mensaje = "Bienvenido, estás autenticado."
    else:
        mensaje = "Bienvenido, por favor inicia sesión para continuar."
    return render(request, 'SISLAB.html', {'mensaje': mensaje})

# Inicio.
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True) #controla la cache. En otras palabras, siempre 
#deben hacer una nueva solicitud al servidor para obtener la versión más reciente.
def inicio(request):
    '''Esto es la pagina principal'''
     # Mensaje que se mostrará en la plantilla
    return render(request, "inicio.html")
