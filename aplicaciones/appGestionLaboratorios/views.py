from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Categorias, Inventario

# Create your views here.
@login_required
def gestionLaboratorios(request):
    categorias = Categorias.objects.all()
    materiales = Inventario.objects.all()
    return render(request, "gestionLaboratorios.html", {'categorias': categorias, 'materiales': materiales})

@login_required
def administracionLaboratorios(request):
    categorias = Categorias.objects.all()
    materiales = Inventario.objects.all()
    return render(request, "administracionLaboratorios.html", {'categorias': categorias, 'materiales': materiales})

