from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Tabla para manejar los usuarios aprobados y denegados
class ApprovedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Usuario aprobado
    date_approved = models.DateTimeField(auto_now_add=True)  # Fecha de aprobación
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="approved_by")  # Admin que lo creó

    def __str__(self):
        return f"{self.user.username} (Aprobado por: {self.created_by.username if self.created_by else 'Desconocido'})"


class DeniedUser(models.Model):
    username = models.CharField(max_length=150)  # Nombre del usuario denegado
    email = models.EmailField()  # Correo electrónico del usuario denegado
    date_denied = models.DateTimeField(auto_now_add=True)  # Fecha de denegación
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="denied_by")  # Admin que lo creó

    def __str__(self):
        return f"{self.username} (Denegado por: {self.created_by.username if self.created_by else 'Desconocido'})"
    

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
    #on delete cascade  asegura que, al eliminar una subcategoría, todos los ítems relacionados 
    #también se eliminen automáticamente.
    id_inventario = models.AutoField(primary_key=True, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True, null=False)
    descripcion = models.TextField(blank=True, null=True)
    cantidad_disponible = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=0.00, 
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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)
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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE)
    presentacion = models.TextField(blank=True, null=True)
    accesorios = models.TextField(blank=True, null=True)
    medidas = models.TextField(blank=True, null=True)
    colores = models.TextField(blank=True, null=True)
    capacidad = models.TextField(blank=True, null=True)
    informacionAdicional = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Datos complementarios para {self.inventario.nombre}"

# Clases para guardar el Inventario General cuando el admin lo desee

# Tabla principal que registra el guardado del Inventario General
class GuardadoInventarioGeneral(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField()
    fecha_guardado = models.DateTimeField(default=now)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - Guardado por {self.usuario.username} ({self.usuario.email}) el {self.fecha_guardado.strftime('%Y-%m-%d %H:%M:%S')}"

# Tabla para almacenar las Categorías guardadas
class CategoriaGuardada(models.Model):
    guardado = models.ForeignKey(GuardadoInventarioGeneral, on_delete=models.CASCADE, related_name='categorias_guardadas')
    nombre_categoria = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre_categoria} ({self.descripcion})"

# Tabla para almacenar las Subcategorías guardadas
class SubCategoriaGuardada(models.Model):
    categoria_guardada = models.ForeignKey(CategoriaGuardada, on_delete=models.CASCADE, related_name='subcategorias_guardadas')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.categoria_guardada.nombre_categoria}"

# Tabla para almacenar los ítems de Inventario guardados
class InventarioGuardado(models.Model):
    subcategoria_guardada = models.ForeignKey(SubCategoriaGuardada, on_delete=models.CASCADE, related_name='inventarios_guardados')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    lote = models.CharField(max_length=36, blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Tabla para almacenar los Detalles Técnicos guardados
class DetalleTecnicoGuardado(models.Model):
    inventario_guardado = models.OneToOneField(InventarioGuardado, on_delete=models.CASCADE, related_name="detalle_tecnico_guardado")
    marca_caracteristica = models.TextField(blank=True, null=True)
    num_cat = models.TextField(blank=True, null=True)
    num_serie = models.TextField(blank=True, null=True)
    modelo = models.TextField(blank=True, null=True)
    codigo = models.TextField(blank=True, null=True)
    articulo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Detalle Técnico guardado para {self.inventario_guardado.nombre}"

# Tabla para almacenar los Datos Complementarios guardados
class DatosComplementariosGuardados(models.Model):
    inventario_guardado = models.OneToOneField(InventarioGuardado, on_delete=models.CASCADE, related_name="datos_complementarios_guardados")
    presentacion = models.TextField(blank=True, null=True)
    accesorios = models.TextField(blank=True, null=True)
    medidas = models.TextField(blank=True, null=True)
    colores = models.TextField(blank=True, null=True)
    capacidad = models.TextField(blank=True, null=True)
    informacionAdicional = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Datos complementarios guardados para {self.inventario_guardado.nombre}"

#LABORATORIOS

#control de horarios en los laboratorios
class HorarioLaboratorio(models.Model):
    laboratorio = models.CharField(max_length=255)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    sin_supervision = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('laboratorio', 'fecha_reserva', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.laboratorio} - {self.fecha_reserva} {self.hora_inicio}-{self.hora_fin}"

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

     conflictos = HorarioLaboratorio.objects.filter(
         laboratorio=self.laboratorio,
         fecha_reserva=self.fecha_reserva,
         hora_inicio__lt=self.hora_fin,
         hora_fin__gt=self.hora_inicio,
     )
     if conflictos.exists():
        raise ValidationError("El laboratorio ya está reservado en el horario solicitado.")


    def aprobar_solicitud(self):
     if self.estado != SolicitudLaboratorio.PENDIENTE:
        raise ValidationError("Solo se pueden aprobar solicitudes pendientes.")

     # Verificar disponibilidad del laboratorio
     conflictos = HorarioLaboratorio.objects.filter(
         laboratorio=self.laboratorio,
         fecha_reserva=self.fecha_reserva,
         hora_inicio__lt=self.hora_fin,
         hora_fin__gt=self.hora_inicio,
     )

     if conflictos.exists():
        raise ValidationError("El laboratorio ya está reservado en el horario solicitado.")

    # Registrar horario de ocupación
     HorarioLaboratorio.objects.create(
        laboratorio=self.laboratorio,
        fecha_reserva=self.fecha_reserva,
        hora_inicio=self.hora_inicio,
        hora_fin=self.hora_fin,
    )

    # Actualizar estado de la solicitud
     self.estado = SolicitudLaboratorio.APROBADA
     self.save()


# Tabla Usos de Ítems en Laboratorios
class UsoItemLaboratorio(models.Model):
    solicitud = models.ForeignKey(SolicitudLaboratorio, on_delete=models.CASCADE)
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    fecha_uso = models.DateField()

    # Guardar cantidad disponible en el momento de la solicitud
    cantidad_disponible_momento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unidad_medida_momento = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        """ Antes de guardar, almacena la cantidad disponible en ese momento """
        if not self.cantidad_disponible_momento:
            self.cantidad_disponible_momento = self.inventario.cantidad_disponible
            self.unidad_medida_momento = self.inventario.unidad_medida
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_uso'], name='idx_fecha_uso'),
        ]

    def __str__(self):
        return f"{self.inventario.nombre} - {self.cantidad_utilizada} - {self.fecha_uso}"

# Tabla Historial de Inventario
class HistorialInventario(models.Model):
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    cantidad_cambiada = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    fecha_cambio = models.DateField()
    tipo_cambio = models.CharField(max_length=50)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    def cantidad_final(self):
        """Calcula la cantidad final después del cambio."""
        if self.tipo_cambio == "entrada":
            return self.cantidad_anterior + self.cantidad_cambiada
        elif self.tipo_cambio == "salida":
            return self.cantidad_anterior - self.cantidad_cambiada
        return self.cantidad_anterior  # En caso de error

    def __str__(self):
        return f"{self.item.nombre} - {self.tipo_cambio} - {self.cantidad_cambiada} - {self.fecha_cambio}"

# Tabla Reportes
class ReporteUsoLaboratorio(models.Model):
    solicitud = models.OneToOneField(SolicitudLaboratorio, on_delete=models.CASCADE, verbose_name="Solicitud Asociada")
    numero_estudiantes = models.PositiveIntegerField(verbose_name="Número de Estudiantes")
    objetivo_practica = models.TextField(verbose_name="Objetivo de la Práctica")
    foto = models.ImageField(upload_to='reportes_fotos/', blank=True, null=True, verbose_name="Foto Adjunta")
    fecha_generacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Generación")

    def __str__(self):
        return f"Reporte para {self.solicitud.laboratorio} - {self.solicitud.usuario.username}"


