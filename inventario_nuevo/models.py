from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.utils.timezone import now
from django.utils import timezone
import os

# --- Catálogos ---
class Categoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Subcategoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Modelo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Presentacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Color(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Capacidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class Accesorios(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class EstadoRecurso(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('no_disponible', 'No disponible'),
        ('baja', 'Dado de baja'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADOS, unique=True)

    def __str__(self):
        return self.get_estado_display()

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    abreviatura = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

#Tabla de Lote
class Lote(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
#Tabla de Medidas de los Productos
class Medida(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "20 mL", "1-25 cm"
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# --- Producto ---
class Producto(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, null=True)
    cantidad_disponible = models.DecimalField(max_digits=8, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=False)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, null=False)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    observacion = models.TextField(blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.ForeignKey(Modelo, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    presentacion = models.ForeignKey(Presentacion, on_delete=models.SET_NULL, null=True, blank=True)
    capacidad = models.ForeignKey(Capacidad, on_delete=models.SET_NULL, null=True, blank=True)
    accesorios = models.ForeignKey(Accesorios, on_delete=models.SET_NULL, null=True, blank=True)
    medida = models.ForeignKey(Medida, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(EstadoRecurso, on_delete=models.PROTECT)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT)  # Sin null ni blank
    codigo = models.CharField(max_length=200, unique=True, blank=True, null=True)
    num_cat = models.CharField("Número de catálogo", max_length=200, unique=True, blank=True, null=True)
    num_serie = models.CharField("Número de serie", max_length=200, unique=True, blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)
    fecha_agregado = models.DateField(auto_now_add=True)
    agregado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='agrega_producto')

    def __str__(self):
        return self.nombre
    
#class InventarioFisico(models.Model):
class InventarioFisico(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('rechazado', 'Rechazado'),
        ('ejecutado', 'Ejecutado'),
        ('cancelado', 'Cancelado'),
    ]

    fecha = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inventarios_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inventario #{self.id} - {self.fecha} - {self.estado}"

class InventarioFisicoDetalle(models.Model):
    inventario = models.ForeignKey(InventarioFisico, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_final = models.DecimalField(max_digits=12, decimal_places=2)
    diferencia = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - Inv #{self.inventario.id}"

class HistorialInventarioFisico(models.Model):
    inventario = models.ForeignKey(InventarioFisico, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad_inicial = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad_final = models.DecimalField(max_digits=8, decimal_places=2)
    diferencia = models.DecimalField(max_digits=8, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateTimeField(auto_now_add=True)  # fecha de creación automática
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_modificacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historial Inv #{self.inventario.id} - {self.producto.nombre} por {self.usuario.username}"
    
#Tabla donde se le da de baja a un producto

class BajaProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='bajas')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    motivo = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_baja = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bajas_realizadas')
    foto = models.ImageField(upload_to='bajas_fotos/', blank=True, null=True)

    def __str__(self):
        return f"Baja de {self.producto.nombre} - {self.cantidad} u."
