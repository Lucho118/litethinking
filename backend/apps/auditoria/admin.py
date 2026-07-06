from django.contrib import admin

from .models import BloqueAuditoriaModel


@admin.register(BloqueAuditoriaModel)
class BloqueAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("indice", "entidad", "entidad_id", "accion", "timestamp")
    list_filter = ("entidad", "accion")
    search_fields = ("entidad_id",)
    ordering = ("indice",)
    readonly_fields = (
        "indice", "timestamp", "entidad", "entidad_id",
        "accion", "datos", "hash_anterior", "hash_actual",
    )

    def has_add_permission(self, request):
        return False  # La auditoría es append-only, nunca se crea desde el admin

    def has_delete_permission(self, request, obj=None):
        return False  # Tampoco se elimina
