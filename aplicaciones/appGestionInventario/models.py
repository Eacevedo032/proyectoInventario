from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,User
from django.forms import ValidationError

from proyectoInventario import settings

# Create your models here.

# Tabla Categoría
class Categoria(models.Model):
    cod_categoria = models.CharField(max_length=36, primary_key=True, default=uuid4, editable=False)
    nombre_categoria = models.CharField(max_length=25)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.nombre_categoria, self.descripcion)

# Tabla Inventario
class Inventario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50, null=True, blank=True)
    vencimiento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(cantidad_disponible__gte=0), name='cantidad_disponible_gte_0')
        ]
        indexes = [
            models.Index(fields=['nombre'], name='idx_nombre_inventario'),
        ]

    def __str__(self):
        return self.nombre

# Tabla Solicitudes de Laboratorios
class SolicitudLaboratorio(models.Model):
    PENDIENTE = 'pendiente'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'
    
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usar el modelo User de Django
    fecha_solicitud = models.DateField(auto_now_add=True)
    laboratorio = models.CharField(max_length=255)
    estado = models.CharField(max_length=50, choices=ESTADOS, default=PENDIENTE)
    fecha_reserva = models.DateField()  # Fecha de la reserva solicitada
    hora_inicio = models.TimeField()  # Hora de inicio de la reserva
    hora_fin = models.TimeField()  # Hora de fin de la reserva

    class Meta:
        indexes = [
            models.Index(fields=['laboratorio'], name='idx_laboratorio_solicitudes'),
        ]

    def __str__(self):
        return f"{self.laboratorio} - {self.usuario.username} - {self.estado}"  # Cambiado a username

    def clean(self):
        # Validar que la hora de inicio sea anterior a la hora de fin
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

# Tabla Usos de Ítems en Laboratorios
class UsoItemLaboratorio(models.Model):
    item = models.ForeignKey(Inventario, on_delete=models.CASCADE)  # Cualquier ítem del inventario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que utilizó el ítem
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_uso = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['fecha_uso'], name='idx_fecha_uso'),#idx_fecha_uso = idx de fecha de uso items en el laboratorio
        ]

    def __str__(self):
        return f"{self.item.nombre} - {self.cantidad_utilizada} - {self.fecha_uso}"

# Tabla Historial de Inventario
class HistorialInventario(models.Model):
    item = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    cantidad_cambiada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cambio = models.DateField()
    tipo_cambio = models.CharField(max_length=50)  # 'entrada' o 'salida'

    def __str__(self):
        return f"{self.item.nombre} - {self.tipo_cambio} - {self.cantidad_cambiada} - {self.fecha_cambio}"

# Tabla Reportes
class Reporte(models.Model):
    tipo_reporte = models.CharField(max_length=50)
    fecha_generacion = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.fecha_generacion}"