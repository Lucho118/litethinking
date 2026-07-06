from django.db import models


class EmpresaModel(models.Model):
    """
    Infraestructura: representa la tabla 'empresas' en PostgreSQL.
    No contiene lógica de negocio — eso vive en domain.entities.Empresa.
    """

    nit = models.CharField(max_length=20, primary_key=True, verbose_name="NIT")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    direccion = models.CharField(max_length=500, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    class Meta:
        db_table = "empresas"
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.nit})"
