from django.db import models
from aplicaciones.appGestionLaboratorios.models import SolicitudLaboratorio

class ReporteUsoLaboratorio(models.Model):
    solicitud = models.OneToOneField('appGestionLaboratorios.SolicitudLaboratorio', on_delete=models.CASCADE, verbose_name="Solicitud Asociada")
    numero_estudiantes = models.PositiveIntegerField(verbose_name="Número de Estudiantes")
    estudiantes_masculinos = models.PositiveIntegerField(verbose_name="Estudiantes Masculinos", default=0)
    estudiantes_femeninos = models.PositiveIntegerField(verbose_name="Estudiantes Femeninos", default=0)
    clase = models.CharField(max_length=100, verbose_name="Clase/Grado")
    asignatura = models.CharField(max_length=100, verbose_name="Asignatura")
    horario_salida_real = models.TimeField(verbose_name="Horario Real de Salida")
    objetivo_practica = models.TextField(verbose_name="Objetivo de la Práctica")
    fecha_generacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Generación")

    def __str__(self):
        return f"Reporte para {self.solicitud.laboratorio} - {self.solicitud.usuario.username}"

class ReporteFoto(models.Model):
    reporte = models.ForeignKey(ReporteUsoLaboratorio, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='reportes_fotos/', max_length=255)

    def __str__(self):
        return f"Foto {self.id} - Reporte {self.reporte.id}"