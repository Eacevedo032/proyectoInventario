from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import UnidadMedida
from .models import EstadoRecurso
from django.utils import timezone
from .models import Categoria, Subcategoria
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from aplicaciones.appGestionInventario .models import UserProfile
from django.db.models.signals import post_migrate
from .models import Ubicacion 

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
    if sender.name == 'inventario_nuevo':  
        ESTADOS_PREDEFINIDOS = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'Mantenimiento (No disponible)'),
        ('baja', 'Dado de baja'),
        ]
        for cod, nombre in ESTADOS_PREDEFINIDOS:
            EstadoRecurso.objects.get_or_create(estado=cod)

#Acá estamos creando las ubicaciones predeterminados al iniciar la app
@receiver(post_migrate)
def crear_ubicaciones_por_defecto(sender, **kwargs):
    if sender.name == 'inventario_nuevo':  
        UBICACIONES_PREDEFINIDAS = [
            'Laboratorio Planta Alta',
            'Laboratorio Planta Baja',
            'Laboratorio Microbiana',
        ]
        for nombre in UBICACIONES_PREDEFINIDAS:
            Ubicacion.objects.get_or_create(nombre=nombre)


#Acá estamos cargando las categorías y subcategorías predeterminadas al iniciar la app
@receiver(post_migrate)
def cargar_categorias_y_subcategorias(sender, **kwargs):
    if sender.name != 'inventario_nuevo': 
        return

    fecha_actual = timezone.now()

    datos = {
        "Medios de Cultivo": ["Medios de Cultivo"],
        "Reactivos": ["Reactivos"],
        "Ph, Tinción y colorantes": ["Phmetros", "Tinciones y Colorantes"],
        "Ácidos, Alcoholes y Preservantes": ["Ácidos, Alcoholes y Preservantes"],
        "Equipos e Instrumentos": ["Equipos de Laboratorio", "Instrumentos de laboratorio"],
        "Cristalería y Porcelana": [
            "Tubos de ensayo", "Erlenmeyers", "Embudos", "Beakers", "Pipetas Serológicas",
            "Probetas", "Crisoles", "Varillas de Vidrio de Borosilicato",
            "Mortero de Porcelana Completo (Mano)", "Balones Aforados 100 ml", "Goteros",
            "Otros", "Otros Tubos", "Buretas", "Cápsula de Porcelana",
            "Embudos de Separación", "Frascos y Recipientes de Vidrio"
        ],
        "Materiales de Limpieza": ["Materiales de Limpieza"],
        "Equipos de Física": ["Equipos de Física"],
        "Material Fungible": [
            "Máscaras", "Guantes", "Placas Petris Desechables",
            "Filtros de Extractor", "Otros Materiales Fungibles",
            "Porta Objetos", "Cubre Objetos", "Gradillas"
        ],
        "Mobiliario de Lab": [
            "Mobiliarios e Instrumentos de Oficina en Planta Baja",
            "Señalizaciones Planta Baja", "Planta Alta", "Señalizaciones Planta Alta"
        ],
        "Rx en Refrigeradora": ["Reactivos en Refrigeradora"]
    }

    for nombre_cat, subcategorias in datos.items():
        categoria, _ = Categoria.objects.get_or_create(
            nombre=nombre_cat,
            defaults={"fecha_creacion": fecha_actual}
        )
        for nombre_sub in subcategorias:
            Subcategoria.objects.get_or_create(
                nombre=nombre_sub,
                defaults={
                    "categoria": categoria,
                    "fecha_creacion": fecha_actual
                }
            )

#Acá estamos creando el perfil de usuario automáticamente al crear un nuevo usuario
# y guardando el perfil de usuario al guardar el usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    username = 'administrador'
    email = 'administrador@unp.edu.ni'
    password = 'unp.1234'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("Usuario administrador creado exitosamente por defecto.")