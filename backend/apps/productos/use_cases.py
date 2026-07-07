from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from domain.entities.precio import Precio
from domain.entities.producto import Producto

from apps.empresas.repositories import EmpresaRepository

from .repositories import ProductoConEmpresa, ProductoRepository, TasaCambioRepository

# Monedas que siempre se incluyen en las respuestas de detalle y listado
_MONEDAS_DEFAULT: list[str] = ["COP", "USD", "EUR"]


@dataclass
class ProductoConPrecios:
    """Resultado de los use cases de lectura: producto + precios en varias monedas."""

    detalle: ProductoConEmpresa
    precios: dict[str, Precio]  # {moneda_ISO: Precio convertido}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _calcular_precios(
    precio_base: Precio,
    tasa_repo: TasaCambioRepository,
    monedas: list[str] = _MONEDAS_DEFAULT,
) -> dict[str, Precio]:
    """
    Devuelve precios en las monedas solicitadas.
    Las tasas se obtienen en una sola consulta a la BD.
    Si no existe tasa para alguna moneda, simplemente no se incluye.
    """
    destinos = [m for m in monedas if m != precio_base.moneda]
    tasas = tasa_repo.obtener_tasas_para(precio_base.moneda, destinos)

    precios: dict[str, Precio] = {precio_base.moneda: precio_base}
    for moneda, tasa in tasas.items():
        precios[moneda] = precio_base.convertir(tasa, moneda)
    return precios


# ── Use Cases ─────────────────────────────────────────────────────────────────

class CrearProductoUseCase:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        empresa_repo: EmpresaRepository,
    ) -> None:
        self.producto_repo = producto_repo
        self.empresa_repo = empresa_repo

    def ejecutar(
        self,
        codigo: str,
        nombre: str,
        caracteristicas: str,
        precio_monto: Decimal,
        precio_moneda: str,
        empresa_nit: str,
        cantidad: int = 0,
    ) -> Producto:
        if self.empresa_repo.obtener(empresa_nit) is None:
            raise ValueError(f"No existe ninguna empresa con NIT '{empresa_nit}'.")
        if self.producto_repo.obtener(codigo) is not None:
            raise ValueError(f"Ya existe un producto con código '{codigo}'.")

        precio = Precio(monto=precio_monto, moneda=precio_moneda)
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            caracteristicas=caracteristicas,
            precio_base=precio,
            empresa_nit=empresa_nit,
            cantidad=cantidad,
        )
        return self.producto_repo.guardar(producto)


class ObtenerProductoConPreciosUseCase:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        tasa_repo: TasaCambioRepository,
    ) -> None:
        self.producto_repo = producto_repo
        self.tasa_repo = tasa_repo

    def ejecutar(
        self,
        codigo: str,
        monedas: list[str] | None = None,
    ) -> ProductoConPrecios | None:
        detalle = self.producto_repo.obtener_con_empresa(codigo)
        if detalle is None:
            return None

        precios = _calcular_precios(
            detalle.producto.precio_base,
            self.tasa_repo,
            monedas or _MONEDAS_DEFAULT,
        )
        return ProductoConPrecios(detalle=detalle, precios=precios)


class ListarProductosUseCase:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        tasa_repo: TasaCambioRepository,
    ) -> None:
        self.producto_repo = producto_repo
        self.tasa_repo = tasa_repo

    def ejecutar(self, empresa_nit: str | None = None) -> list[ProductoConPrecios]:
        detalles = self.producto_repo.listar(empresa_nit)

        # Obtener todas las monedas base únicas y sus tasas en bloque (evita N+1)
        monedas_base = {d.producto.precio_base.moneda for d in detalles}
        todas_las_tasas: dict[str, dict[str, Decimal]] = {
            origen: self.tasa_repo.obtener_tasas_para(
                origen, [m for m in _MONEDAS_DEFAULT if m != origen]
            )
            for origen in monedas_base
        }

        result: list[ProductoConPrecios] = []
        for detalle in detalles:
            precio_base = detalle.producto.precio_base
            tasas = todas_las_tasas.get(precio_base.moneda, {})
            precios: dict[str, Precio] = {precio_base.moneda: precio_base}
            for moneda, tasa in tasas.items():
                precios[moneda] = precio_base.convertir(tasa, moneda)
            result.append(ProductoConPrecios(detalle=detalle, precios=precios))

        return result


class ActualizarProductoUseCase:
    def __init__(
        self,
        producto_repo: ProductoRepository,
        empresa_repo: EmpresaRepository,
    ) -> None:
        self.producto_repo = producto_repo
        self.empresa_repo = empresa_repo

    def ejecutar(
        self,
        codigo: str,
        nombre: str,
        caracteristicas: str,
        precio_monto: Decimal,
        precio_moneda: str,
        empresa_nit: str,
        cantidad: int = 0,
    ) -> Producto:
        if self.producto_repo.obtener(codigo) is None:
            raise ValueError(f"No existe ningún producto con código '{codigo}'.")
        if self.empresa_repo.obtener(empresa_nit) is None:
            raise ValueError(f"No existe ninguna empresa con NIT '{empresa_nit}'.")

        precio = Precio(monto=precio_monto, moneda=precio_moneda)
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            caracteristicas=caracteristicas,
            precio_base=precio,
            empresa_nit=empresa_nit,
            cantidad=cantidad,
        )
        return self.producto_repo.guardar(producto)


class EliminarProductoUseCase:
    def __init__(self, producto_repo: ProductoRepository) -> None:
        self.producto_repo = producto_repo

    def ejecutar(self, codigo: str) -> None:
        if self.producto_repo.obtener(codigo) is None:
            raise ValueError(f"No existe ningún producto con código '{codigo}'.")
        self.producto_repo.eliminar(codigo)
