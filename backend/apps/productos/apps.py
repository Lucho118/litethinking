from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productos"
    verbose_name = "Productos"

    def ready(self):
        import sys
        print("[ProductosConfig] ready() ejecutado — conectando signal de vectorización", file=sys.stderr, flush=True)
        from apps.productos.signals import conectar_signal_vectorizacion
        conectar_signal_vectorizacion()
