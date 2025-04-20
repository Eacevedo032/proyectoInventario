from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
import os

#Perfil de usuario, sirve para editar el perfil y la parte del inventario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def delete_profile_picture(self):
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            os.remove(self.profile_picture.path)
            self.profile_picture.delete(save=False)

# Tabla para manejar los usuarios aprobados y denegados
class ApprovedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Usuario aprobado
    date_approved = models.DateTimeField(auto_now_add=True)  # Fecha de aprobación
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="approved_by")  # Admin que lo creó

    def __str__(self):
        return f"{self.user.username} (Aprobado por: {self.created_by.username if self.created_by else 'Desconocido'})"

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
        return f"{self.nombre} - {self.usuario.username} ({self.fecha_guardado.strftime('%Y-%m-%d %H:%M:%S')})"

# Nueva tabla para categorías/subcategorías (snapshots)
class CategoriaSubcategoriaSnapshot(models.Model): 
    guardado = models.ForeignKey(GuardadoInventarioGeneral, on_delete=models.CASCADE, related_name='categorias_snapshot')
    nombre_categoria = models.CharField(max_length=100)
    descripcion_categoria = models.CharField(max_length=255)
    nombre_subcategoria = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('guardado', 'nombre_categoria', 'nombre_subcategoria')
        verbose_name = "Categoría/Subcategoría (Snapshot)"
    
    def __str__(self):
        return f"{self.nombre_categoria} - {self.nombre_subcategoria}"

# Tabla de ítems (snapshots) 
class InventarioGuardado(models.Model):  
    categoria_subcategoria = models.ForeignKey(CategoriaSubcategoriaSnapshot, on_delete=models.CASCADE, related_name='items_snapshot') 
    # campos actuales:
    nombre = models.CharField(max_length=100)
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
    # Campos técnicos:
    marca_caracteristica = models.TextField(blank=True, null=True)
    num_cat = models.TextField(blank=True, null=True)
    num_serie = models.TextField(blank=True, null=True)
    modelo = models.TextField(blank=True, null=True)
    codigo = models.TextField(blank=True, null=True)
    articulo = models.TextField(blank=True, null=True)
    # Datos complementarios:
    presentacion = models.TextField(blank=True, null=True)
    accesorios = models.TextField(blank=True, null=True)
    medidas = models.TextField(blank=True, null=True)
    colores = models.TextField(blank=True, null=True)
    capacidad = models.TextField(blank=True, null=True)
    informacionAdicional = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('categoria_subcategoria', 'nombre', 'lote')
        verbose_name = "Ítem Guardado (Snapshot)"
    
    def __str__(self):
        return f"{self.nombre} (Lote: {self.lote})"
    
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
    EN_REVISION = 'en_revision'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'
    
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (EN_REVISION, 'En revisión'),
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


    def enviar_solicitud(self):
        """Método para cambiar el estado a 'en revisión'."""
        if self.estado != self.PENDIENTE:
            raise ValidationError("Solo se pueden enviar solicitudes pendientes.")
        self.estado = self.EN_REVISION
        self.save()

    def aprobar_solicitud(self):
        """Método para aprobar la solicitud solo si está en revisión."""
        if self.estado != self.EN_REVISION:
            raise ValidationError("Solo se pueden aprobar solicitudes en revisión.")
        
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
        self.estado = self.APROBADA
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
        return f"{self.inventario.nombre} - {self.tipo_cambio} - {self.cantidad_cambiada} - {self.fecha_cambio}"

class ReporteUsoLaboratorio(models.Model):
    solicitud = models.OneToOneField('SolicitudLaboratorio', on_delete=models.CASCADE, verbose_name="Solicitud Asociada")
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
    
from .signals import *


class ReporteFoto(models.Model):
    reporte = models.ForeignKey(ReporteUsoLaboratorio, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='reportes_fotos/', max_length=255)

    def __str__(self):
        return f"Foto {self.id} - Reporte {self.reporte.id}"
