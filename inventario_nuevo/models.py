from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.utils.timezone import now
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
        ('prestado', 'Prestado (No disponible)'),
        ('mantenimiento', 'Mantenimiento (No disponible)'),
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

# --- Movimiento de Producto ---
class MovimientoProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    usuario_asociado = models.ForeignKey(User, on_delete=models.PROTECT, related_name='usuario_asociado')
    gestionado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='gestor_movimiento')
    tipo_movimiento = models.CharField(max_length=100)
    cantidad_movida = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    estado_resultante = models.ForeignKey(EstadoRecurso, on_delete=models.PROTECT)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Movimiento: {self.tipo_movimiento} - {self.producto.nombre} ({self.fecha_movimiento.strftime('%d-%m-%Y %H:%M')})"

# --- Control de Inventario Físico ---
class InventarioFisico(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad_teorica = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad_real = models.DecimalField(max_digits=8, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    fecha_revision = models.DateTimeField(auto_now_add=True)
    revisado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    observacion = models.TextField(blank=True, null=True)

    def diferencia(self):
        return self.cantidad_real - self.cantidad_teorica

    def __str__(self):
        return f"Inventario físico de {self.producto.nombre} - {self.fecha_revision.strftime('%d-%m-%Y')}"

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
 
# DIFERENCIAS DE INVENTARIO, TRANSFERENCIAS, CIERRE DE INVENTARIO
class InventarioDiario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    fecha = models.DateField()
    cantidad_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_diferencia(self):
        self.diferencia = self.cantidad_final - self.cantidad_inicial
        self.save()

    def __str__(self):
        return f"{self.producto.nombre} - {self.fecha} - {self.usuario.username if self.usuario else 'Sin usuario'}"

class TransferenciaProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Usuario que hizo la transferencia
    fecha_transferencia = models.DateField(auto_now_add=True)  # Fecha automática
    estado_destino = models.CharField(max_length=50, choices=[
        ("Dado de baja", "Dado de baja"),
        ("Mantenimiento", "Mantenimiento"),
        ("No Disponible", "No Disponible"),
        ("Prestado", "Prestado"),
        ("Ingreso", "Ingreso"),
    ])
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Cantidad transferida
    motivo = models.TextField(blank=True, null=True)  #Explicación de la transferencia
    observacion = models.TextField(blank=True, null=True)  #Nota adicional sobre el movimiento

    def __str__(self):
        return f"{self.usuario.username} transfirió {self.cantidad} de {self.producto.nombre} a {self.estado_destino} ({self.fecha_transferencia})"
    
