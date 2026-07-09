from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productos"
    verbose_name = "Productos"

    def ready(self):
        import sys
        print("[ProductosConfig] ready() — importando signals", file=sys.stderr, flush=True)
        import apps.productos.signals  # noqa: F401 — registra @receiver al importar
