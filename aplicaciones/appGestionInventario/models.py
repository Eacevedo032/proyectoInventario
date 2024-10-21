from django.db import models

# Create your models here.

class Categorias(models.Model):
    cod_categoria = models.CharField(max_length=5, primary_key=True)
    nombre_categoria = models.CharField(max_length=25)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.nombre_categoria, self.descripcion)
