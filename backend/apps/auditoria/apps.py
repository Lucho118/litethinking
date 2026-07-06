from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auditoria"
    verbose_name = "Auditoría"

    def ready(self) -> None:
        # Conecta los signals de post_save/post_delete al iniciar la app
        import apps.auditoria.signals  # noqa: F401
