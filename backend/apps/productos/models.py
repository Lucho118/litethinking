from django.db import models

from apps.empresas.models import EmpresaModel


class ProductoModel(models.Model):
    """
    Infraestructura: tabla 'productos' en PostgreSQL.
    La FK a EmpresaModel usa PROTECT para evitar borrar una empresa
    que tenga productos sin manejar la situación explícitamente.
    """

    codigo = models.CharField(max_length=50, primary_key=True, verbose_name="Código")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    caracteristicas = models.TextField(blank=True, verbose_name="Características")
    precio_base = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Precio base")
    moneda_base = models.CharField(max_length=3, default="COP", verbose_name="Moneda base")
    empresa = models.ForeignKey(
        EmpresaModel,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Empresa",
    )

    class Meta:
        db_table = "productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.codigo})"


class TasaCambioModel(models.Model):
    """
    Tasas de cambio almacenadas manualmente en BD.
    Decisión: BD (no archivo de config) porque las tasas cambian frecuentemente
    y deben poder actualizarse sin redeploy.
    En producción un job periódico las sincronizaría con exchangerate-api.com.
    """

    moneda_origen = models.CharField(max_length=3, verbose_name="Moneda origen")
    moneda_destino = models.CharField(max_length=3, verbose_name="Moneda destino")
    tasa = models.DecimalField(max_digits=20, decimal_places=8, verbose_name="Tasa")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        db_table = "tasas_cambio"
        unique_together = [("moneda_origen", "moneda_destino")]
        verbose_name = "Tasa de cambio"
        verbose_name_plural = "Tasas de cambio"

    def __str__(self) -> str:
        return f"1 {self.moneda_origen} = {self.tasa} {self.moneda_destino}"
