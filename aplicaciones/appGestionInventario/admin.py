from django.contrib import admin
from .models import Categoria,Inventario,SolicitudLaboratorio,UsoItemLaboratorio, SubCategoria, HorarioLaboratorio

# Create your models here.
admin.site.register(Categoria)
admin.site.register(SubCategoria)
admin.site.register(Inventario)
admin.site.register(SolicitudLaboratorio)
admin.site.register(UsoItemLaboratorio)
admin.site.register(HorarioLaboratorio)

class HorarioLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'fecha_reserva', 'hora_inicio', 'hora_fin')
    list_filter = ('laboratorio', 'fecha_reserva')
