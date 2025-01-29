from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from .categorias import *
from .subcategorias import *
from .inventario import *
from .Usuarios import *
from .registrar_cambio_inventario import *

# Inicio.
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True) #controla la cache. En otras palabras, siempre 
#deben hacer una nueva solicitud al servidor para obtener la versión más reciente.
def inicio(request):
    '''Esto es la pagina principal'''
     # Mensaje que se mostrará en la plantilla
    return render(request, "inicio.html")

