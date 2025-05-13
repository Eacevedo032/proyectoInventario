# Register your models here.
from django.contrib import admin
from .models import SolicitudLaboratorio,UsoItemLaboratorio, HorarioLaboratorio

# Create your models here.
admin.site.register(SolicitudLaboratorio)
admin.site.register(UsoItemLaboratorio)
admin.site.register(HorarioLaboratorio)

class HorarioLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'fecha_reserva', 'hora_inicio', 'hora_fin')
    list_filter = ('laboratorio', 'fecha_reserva')