from django.db import models


class BloqueAuditoriaModel(models.Model):
    """
    Persiste cada bloque de la cadena de auditoría.
    hash_actual es único e indexado para detección rápida de duplicados.
    No se permite UPDATE ni DELETE sobre esta tabla (solo INSERT) — la
    inmutabilidad debe hacerse cumplir a nivel de aplicación y de BD.
    """

    indice = models.PositiveIntegerField(unique=True, db_index=True, verbose_name="Índice")
    timestamp = models.DateTimeField(verbose_name="Timestamp")
    entidad = models.CharField(max_length=50, verbose_name="Entidad")       # "Empresa" | "Producto"
    entidad_id = models.CharField(max_length=50, db_index=True, verbose_name="ID entidad")
    accion = models.CharField(max_length=10, verbose_name="Acción")         # "CREAR" | "EDITAR" | "ELIMINAR"
    datos = models.JSONField(verbose_name="Datos")
    hash_anterior = models.CharField(max_length=64, verbose_name="Hash anterior")
    hash_actual = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="Hash actual")

    class Meta:
        db_table = "auditoria_cadena"
        ordering = ["indice"]
        verbose_name = "Bloque de auditoría"
        verbose_name_plural = "Bloques de auditoría"

    def __str__(self) -> str:
        return f"[{self.indice}] {self.accion} {self.entidad} {self.entidad_id}"
