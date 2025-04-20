from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import UnidadMedida
from .models import EstadoRecurso

@receiver(post_migrate)
def cargar_unidades_predeterminadas(sender, **kwargs):
    unidades = [
        {"nombre": "Unidades", "abreviatura": "Unidad", "descripcion": "Productos contables unitarios"},
        {"nombre": "Kilogramo", "abreviatura": "kg", "descripcion": "Unidad de masa"},
        {"nombre": "Gramo", "abreviatura": "g", "descripcion": "Unidad de masa pequeña"},
        {"nombre": "Miligramo", "abreviatura": "mg", "descripcion": "Unidad de masa muy pequeña"},
        {"nombre": "Libra", "abreviatura": "lb", "descripcion": "Unidad de masa imperial"},
        {"nombre": "Litro", "abreviatura": "L", "descripcion": "Unidad de volumen"},
        {"nombre": "Mililitro", "abreviatura": "mL", "descripcion": "Volumen pequeño"},
        {"nombre": "Centímetro cúbico", "abreviatura": "cm³", "descripcion": "Equivale a un mL"},
        {"nombre": "Metro cúbico", "abreviatura": "m³", "descripcion": "Volumen grande"},
        {"nombre": "Galón", "abreviatura": "gal", "descripcion": "Unidad de volumen imperial"},
        {"nombre": "Metro", "abreviatura": "m", "descripcion": "Unidad de longitud"},
        {"nombre": "Milímetro", "abreviatura": "mm", "descripcion": "Unidad pequeña de longitud"},
        {"nombre": "Centímetro", "abreviatura": "cm", "descripcion": "Unidad de longitud"},
        {"nombre": "Pulgada", "abreviatura": "in", "descripcion": "Unidad de longitud imperial"},
    ]

    for unidad in unidades:
        UnidadMedida.objects.get_or_create(
            abreviatura=unidad["abreviatura"],
            defaults={
                "nombre": unidad["nombre"],
                "descripcion": unidad["descripcion"],
            }
        )

@receiver(post_migrate)
def crear_estados_recurso(sender, **kwargs):
    if sender.name == 'inventario_nuevo':  # Nombre de la app
        ESTADOS_PREDEFINIDOS = [
            ('disponible', 'Disponible'),
            ('prestado', 'Prestado'),
            ('baja', 'Dado de Baja'),
            ('mantenimiento', 'Mantenimiento'),
            ('no_disponible', 'No Disponible'),
        ]
        for cod, nombre in ESTADOS_PREDEFINIDOS:
            EstadoRecurso.objects.get_or_create(estado=cod)