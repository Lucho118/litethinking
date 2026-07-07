from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from django.db.models import Count

from domain.entities.precio import Precio
from domain.entities.producto import Producto

from .models import ConsultaProductoModel, ProductoModel, TasaCambioModel


@dataclass
class ProductoConEmpresa:
    """
    Read model de infraestructura: agrega el nombre de la empresa al producto
    para evitar que el frontend haga una consulta extra.
    No pertenece al dominio — vive en la capa de repositorio.
    """

    producto: Producto
    empresa_nombre: str


class ProductoRepository:

    def guardar(self, producto: Producto) -> Producto:
        model, _ = ProductoModel.objects.update_or_create(
            codigo=producto.codigo,
            defaults={
                "nombre": producto.nombre,
                "caracteristicas": producto.caracteristicas,
                "precio_base": producto.precio_base.monto,
                "moneda_base": producto.precio_base.moneda,
                "empresa_id": producto.empresa_nit,
                "cantidad": producto.cantidad,
            },
        )
        return self._to_entity(model)

    def obtener(self, codigo: str) -> Producto | None:
        try:
            return self._to_entity(ProductoModel.objects.get(codigo=codigo))
        except ProductoModel.DoesNotExist:
            return None

    def obtener_con_empresa(self, codigo: str) -> ProductoConEmpresa | None:
        try:
            model = ProductoModel.objects.select_related("empresa").get(codigo=codigo)
            return ProductoConEmpresa(
                producto=self._to_entity(model),
                empresa_nombre=model.empresa.nombre,
            )
        except ProductoModel.DoesNotExist:
            return None

    def listar(self, empresa_nit: str | None = None) -> list[ProductoConEmpresa]:
        qs = ProductoModel.objects.select_related("empresa").order_by("nombre")
        if empresa_nit:
            qs = qs.filter(empresa_id=empresa_nit)
        return [
            ProductoConEmpresa(producto=self._to_entity(m), empresa_nombre=m.empresa.nombre)
            for m in qs
        ]

    def eliminar(self, codigo: str) -> bool:
        deleted, _ = ProductoModel.objects.filter(codigo=codigo).delete()
        return deleted > 0

    def contar(self) -> int:
        return ProductoModel.objects.count()

    def distribucion_por_precio(self) -> list[dict]:
        """
        Devuelve cantidad de productos por rango de precio base en USD equiv.
        Los rangos son: < 50, 50-200, > 200 (en la moneda almacenada).
        Para simplificar, el rango se aplica directamente sobre precio_base
        independientemente de la moneda.
        """
        total = ProductoModel.objects.count()
        if total == 0:
            return []
        menos_50 = ProductoModel.objects.filter(precio_base__lt=50).count()
        entre_50_200 = ProductoModel.objects.filter(
            precio_base__gte=50, precio_base__lte=200
        ).count()
        mas_200 = ProductoModel.objects.filter(precio_base__gt=200).count()
        return [
            {"rango": "Menos de $50", "cantidad": menos_50},
            {"rango": "$50 – $200", "cantidad": entre_50_200},
            {"rango": "Más de $200", "cantidad": mas_200},
        ]

    @staticmethod
    def _to_entity(model: ProductoModel) -> Producto:
        return Producto(
            codigo=model.codigo,
            nombre=model.nombre,
            caracteristicas=model.caracteristicas,
            precio_base=Precio(monto=model.precio_base, moneda=model.moneda_base),
            empresa_nit=model.empresa_id,
            cantidad=model.cantidad,
        )


@dataclass
class ProductoMasConsultado:
    codigo: str
    nombre: str
    total_consultas: int


class ConsultaProductoRepository:
    """Accede al contador de consultas registrado por el microservicio ai-agent."""

    def producto_mas_consultado(self) -> Optional[ProductoMasConsultado]:
        top = (
            ConsultaProductoModel.objects
            .order_by("-total_consultas")
            .select_related()  # no FK, but keeps interface consistent
            .first()
        )
        if top is None:
            return None
        # Intentar obtener el nombre desde ProductoModel
        try:
            nombre = ProductoModel.objects.get(codigo=top.codigo).nombre
        except ProductoModel.DoesNotExist:
            nombre = top.codigo
        return ProductoMasConsultado(
            codigo=top.codigo,
            nombre=nombre,
            total_consultas=top.total_consultas,
        )


class TasaCambioRepository:

    def obtener_tasas_para(self, origen: str, destinos: list[str]) -> dict[str, Decimal]:
        """Devuelve {moneda_destino: tasa} en una sola consulta a la BD."""
        if not destinos:
            return {}
        tasas = TasaCambioModel.objects.filter(
            moneda_origen=origen,
            moneda_destino__in=destinos,
        )
        return {t.moneda_destino: t.tasa for t in tasas}
