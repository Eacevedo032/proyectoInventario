from django.contrib import admin
from .models import Categoria,Inventario,SolicitudLaboratorio,UsoItemLaboratorio, SubCategoria

# Create your models here.
admin.site.register(Categoria)
admin.site.register(SubCategoria)
admin.site.register(Inventario)
admin.site.register(SolicitudLaboratorio)
admin.site.register(UsoItemLaboratorio)