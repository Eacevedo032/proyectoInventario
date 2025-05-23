from django.db import models
from django.contrib.auth.models import User
from inventario_nuevo.models import Producto
from django.core.exceptions import ValidationError

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
    COMPLETADO = 'Completado'
    
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (EN_REVISION, 'En revisión'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
        (COMPLETADO, 'Completado')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField(auto_now_add=True)
    laboratorio = models.CharField(max_length=255)
    clase = models.CharField(max_length=100, verbose_name="Clase/Grado")
    asignatura = models.CharField(max_length=100, verbose_name="Asignatura")
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    objetivo_practica = models.TextField(verbose_name="Objetivo de la Práctica")
    estado = models.CharField(max_length=50, choices=ESTADOS, default=PENDIENTE)
    
    tiene_recursos = models.BooleanField(default=False, verbose_name="¿Tiene recursos asignados?")

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

#Tabla Uso de Items de inventario
class SolicitudProductosInventario(models.Model):
    PENDIENTE = 'pendiente'
    EN_REVISION = 'en_revision'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'

    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (EN_REVISION, 'En Revisión'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(max_length=50, null=True, blank=True)
    fecha_uso = models.DateField()
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)

    cantidad_disponible_momento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unidad_medida_momento = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_uso'], name='idx_fecha_solicitud_general'),
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.usuario.username} - {self.estado}"

    def save(self, *args, **kwargs):
        """ Antes de guardar, almacena la cantidad disponible en ese momento """
        if not self.cantidad_disponible_momento:
            self.cantidad_disponible_momento = self.producto.cantidad_disponible
            self.unidad_medida_momento = str(self.producto.unidad_medida)
        super().save(*args, **kwargs)

    def enviar_solicitud(self):
        if self.estado != self.PENDIENTE:
            raise ValidationError("Solo se pueden enviar solicitudes pendientes.")
        self.estado = self.EN_REVISION
        self.save()

    def aprobar_solicitud(self):
        if self.estado != self.EN_REVISION:
            raise ValidationError("Solo se pueden aprobar solicitudes en revisión.")
        self.estado = self.APROBADA
        self.save()

    def rechazar_solicitud(self):
        if self.estado != self.EN_REVISION:
            raise ValidationError("Solo se pueden rechazar solicitudes en revisión.")
        self.estado = self.RECHAZADA
        self.save()

# Tabla Usos de Ítems en Laboratorios
class UsoItemLaboratorio(models.Model):
    solicitud = models.ForeignKey(SolicitudLaboratorio, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
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
            self.cantidad_disponible_momento = self.producto.cantidad_disponible
            self.unidad_medida_momento = str(self.producto.unidad_medida)

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['fecha_uso'], name='idx_fecha_uso'),
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_utilizada} - {self.fecha_uso}"

# Tabla Historial de Inventario
class HistorialInventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
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
        return f"{self.producto.nombre} - {self.tipo_cambio} - {self.cantidad_cambiada} - {self.fecha_cambio}"
