from django.apps import AppConfig

class AppGestionInventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.appGestionInventario'

def ready(self):
    import appGestionInventario.signals  #Carga de las señales para la foto de perfil de usuario

