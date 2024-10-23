from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def gestionLaboratorios(request):
    '''Esto es la pagina principal'''
    return render(request, "gestionLaboratorios.html")
