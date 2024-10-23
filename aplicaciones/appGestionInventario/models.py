from django.db import models

# Create your models here.

class Categorias(models.Model):
    cod_categoria = models.CharField(max_length=5, primary_key=True)
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
    Categorias = models.ForeignKey(Categorias, on_delete=models.CASCADE)
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