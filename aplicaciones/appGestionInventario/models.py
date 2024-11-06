from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

# Tabla Categoria
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre_categoria} ({self.descripcion})"

# Tabla Subcategoría
class SubCategoria(models.Model):
    id_subcategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre_categoria}"

# Tabla Inventario
class Inventario(models.Model):
    id_inventario = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, null=True, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    presentacion = models.TextField(null=True, blank=True)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    codigo = models.CharField(max_length=50, null=True, blank=True, unique=True)
    vencimiento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    lote = models.CharField(max_length=36, null=True, blank=True)  
    marca_caracteristica = models.TextField(null=True, blank=True)
    num_cat = models.CharField(max_length=50, null=True, blank=True)
    num_serie = models.CharField(max_length=25, null=True, blank=True)
    modelo = models.CharField(max_length=25, null=True, blank=True)
    accesorios = models.TextField(null=True, blank=True)
    medidas = models.CharField(max_length=50, null=True, blank=True)
    articulo = models.CharField(max_length=50, null=True, blank=True)
    colores = models.CharField(max_length=50, null=True, blank=True)
    capacidad = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.cantidad_disponible} unidades"

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

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
    laboratorio = models.CharField(max_length=255)
    estado = models.CharField(max_length=50, choices=ESTADOS, default=PENDIENTE)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        indexes = [
            models.Index(fields=['laboratorio'], name='idx_laboratorio_solicitudes'),
        ]

    def __str__(self):
        return f"{self.laboratorio} - {self.usuario.username} - {self.estado}"

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

# Tabla Usos de Ítems en Laboratorios
class UsoItemLaboratorio(models.Model):
    item = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_uso = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['fecha_uso'], name='idx_fecha_uso'),
        ]

    def __str__(self):
        return f"{self.item.nombre} - {self.cantidad_utilizada} - {self.fecha_uso}"

# Tabla Historial de Inventario
class HistorialInventario(models.Model):
    item = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    cantidad_cambiada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cambio = models.DateField()
    tipo_cambio = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.item.nombre} - {self.tipo_cambio} - {self.cantidad_cambiada} - {self.fecha_cambio}"

# Tabla Reportes
class Reporte(models.Model):
    tipo_reporte = models.CharField(max_length=50)
    fecha_generacion = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.fecha_generacion}"
