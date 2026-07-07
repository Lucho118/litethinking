from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from domain.entities.precio import Precio
from domain.entities.producto import Producto

from .models import ProductoModel, TasaCambioModel


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
