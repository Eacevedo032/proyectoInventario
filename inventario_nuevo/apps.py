from django.apps import AppConfig

class InventarioNuevoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario_nuevo'

    def ready(self):
        import inventario_nuevo.signals


