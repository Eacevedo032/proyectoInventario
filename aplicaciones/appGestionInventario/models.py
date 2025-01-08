from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator

# Tabla Categoria
class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre_categoria} ({self.descripcion})"

# Tabla Subcategoría
class SubCategoria(models.Model):
    id_subcategoria = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre_categoria}"

class Inventario(models.Model):
    #id_inventario = models.AutoField(primary_key=True) esto se crea solo sin necesidad de escribirlo
    #on delete cascade  asegura que, al eliminar una subcategoría, todos los ítems relacionados 
    #también se eliminen automáticamente.
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=100, unique=True, null=False)
    descripcion = models.TextField(blank=True, null=True)
    cantidad_disponible = models.FloatField(
         default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Cantidad Disponible"
    )
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    lote = models.CharField(max_length=36, blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

#Con OneToOneField en DetalleTecnico, se garantiza que:
#Cada registro en DetalleTecnico está vinculado a un único registro en Inventario.
#Cada registro en Inventario tiene, como máximo, un único registro en DetalleTecnico.

class DetalleTecnico(models.Model):
    inventario = models.OneToOneField(Inventario, on_delete=models.CASCADE, related_name="detalle_tecnico")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, null=True)
    marca_caracteristica = models.TextField(blank=True, null=True)
    num_cat = models.TextField(blank=True, null=True)
    num_serie = models.TextField(blank=True, null=True)
    modelo = models.TextField(blank=True, null=True)
    codigo = models.TextField(blank=True, null=True)
    articulo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detalle Técnico para {self.inventario.nombre}"


class DatosComplementarios(models.Model):
    inventario = models.OneToOneField(Inventario, on_delete=models.CASCADE, related_name="datos_complementarios")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, null=True)
    presentacion = models.TextField(blank=True, null=True)
    accesorios = models.TextField(blank=True, null=True)
    medidas = models.TextField(blank=True, null=True)
    colores = models.TextField(blank=True, null=True)
    capacidad = models.TextField(blank=True, null=True)
    informacionAdicional = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Datos complementarios para {self.inventario.nombre}"


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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
    laboratorio = models.CharField(max_length=255)
    estado = models.CharField(max_length=50, choices=ESTADOS, default=PENDIENTE)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        indexes = [
            models.Index(fields=['laboratorio'], name='idx_laboratorio_solicitudes'),
        ]

    def __str__(self):
        return f"{self.laboratorio} - {self.usuario.username} - {self.estado}"
    def __str__(self):
        return f"{self.laboratorio} - {self.usuario.username} - {self.estado}"

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

    def aprobar_solicitud(self):
        if self.estado != SolicitudLaboratorio.PENDIENTE:
            raise ValidationError("Solo se pueden aprobar solicitudes pendientes.")
        
        usos = UsoItemLaboratorio.objects.filter(solicitud=self)
        for uso in usos:
            inventario_item = uso.item
            if inventario_item.cantidad_disponible >= uso.cantidad_utilizada:
                inventario_item.cantidad_disponible -= uso.cantidad_utilizada
                inventario_item.save()

                # Registrar en el historial
                HistorialInventario.objects.create(
                    item=inventario_item,
                    cantidad_cambiada=uso.cantidad_utilizada,
                    fecha_cambio=timezone.now(),
                    tipo_cambio='salida'
                )
            else:
                raise ValidationError(f"No hay suficiente cantidad de {inventario_item.nombre} en inventario.")

        self.estado = SolicitudLaboratorio.APROBADA
        self.save()

    def aprobar_solicitud(self):
        if self.estado != SolicitudLaboratorio.PENDIENTE:
            raise ValidationError("Solo se pueden aprobar solicitudes pendientes.")
        
        usos = UsoItemLaboratorio.objects.filter(solicitud=self)
        for uso in usos:
            inventario_item = uso.item
            if inventario_item.cantidad_disponible >= uso.cantidad_utilizada:
                inventario_item.cantidad_disponible -= uso.cantidad_utilizada
                inventario_item.save()

                # Registrar en el historial
                HistorialInventario.objects.create(
                    item=inventario_item,
                    cantidad_cambiada=uso.cantidad_utilizada,
                    fecha_cambio=timezone.now(),
                    tipo_cambio='salida'
                )
            else:
                raise ValidationError(f"No hay suficiente cantidad de {inventario_item.nombre} en inventario.")

        self.estado = SolicitudLaboratorio.APROBADA
        self.save()

# Tabla Usos de Ítems en Laboratorios
class UsoItemLaboratorio(models.Model):
    solicitud = models.ForeignKey(SolicitudLaboratorio, on_delete=models.CASCADE)
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
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
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
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



