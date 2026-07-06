from decimal import Decimal

import pytest

from domain.entities.precio import Precio
from domain.entities.producto import Producto


# ── Precio: value object ──────────────────────────────────────────────────────

def test_precio_valido():
    p = Precio(monto=Decimal("2500000.00"), moneda="COP")
    assert p.monto == Decimal("2500000.00")
    assert p.moneda == "COP"


def test_precio_monto_cero_es_valido():
    p = Precio(monto=Decimal("0"), moneda="USD")
    assert p.monto == Decimal("0")


def test_precio_negativo_lanza_error():
    with pytest.raises(ValueError, match="negativo"):
        Precio(monto=Decimal("-1"), moneda="COP")


def test_precio_moneda_invalida_lanza_error():
    with pytest.raises(ValueError, match="Moneda no soportada"):
        Precio(monto=Decimal("100"), moneda="GBP")


def test_precio_es_inmutable():
    p = Precio(monto=Decimal("100"), moneda="COP")
    with pytest.raises(Exception):
        p.monto = Decimal("200")  # frozen dataclass


def test_convertir_precio():
    precio_cop = Precio(monto=Decimal("4166.67"), moneda="COP")
    precio_usd = precio_cop.convertir(tasa=Decimal("0.000240"), moneda_destino="USD")
    assert precio_usd.moneda == "USD"
    assert precio_usd.monto == Decimal("1.00")


def test_convertir_precio_redondea_a_dos_decimales():
    precio = Precio(monto=Decimal("1000"), moneda="COP")
    convertido = precio.convertir(tasa=Decimal("0.000241"), moneda_destino="USD")
    assert len(str(convertido.monto).split(".")[-1]) <= 2


def test_convertir_tasa_cero_lanza_error():
    precio = Precio(monto=Decimal("1000"), moneda="COP")
    with pytest.raises(ValueError, match="positivo"):
        precio.convertir(tasa=Decimal("0"), moneda_destino="USD")


def test_convertir_tasa_negativa_lanza_error():
    precio = Precio(monto=Decimal("1000"), moneda="COP")
    with pytest.raises(ValueError, match="positivo"):
        precio.convertir(tasa=Decimal("-0.5"), moneda_destino="USD")


# ── Producto: entity ──────────────────────────────────────────────────────────

def _precio_cop(monto="2500000.00"):
    return Precio(monto=Decimal(monto), moneda="COP")


def test_producto_valido():
    p = Producto(
        codigo="PROD-001",
        nombre="Laptop X1",
        caracteristicas="16GB RAM, 512GB SSD",
        precio_base=_precio_cop(),
        empresa_nit="830514226-6",
    )
    assert p.codigo == "PROD-001"
    assert p.empresa_nit == "830514226-6"


@pytest.mark.parametrize("codigo", ["", "   "])
def test_codigo_vacio_lanza_error(codigo):
    with pytest.raises(ValueError, match="código"):
        Producto(
            codigo=codigo, nombre="X", caracteristicas="",
            precio_base=_precio_cop(), empresa_nit="830514226-6",
        )


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio_lanza_error(nombre):
    with pytest.raises(ValueError, match="nombre"):
        Producto(
            codigo="PROD-001", nombre=nombre, caracteristicas="",
            precio_base=_precio_cop(), empresa_nit="830514226-6",
        )


def test_producto_empresa_es_solo_nit():
    """El dominio solo almacena el NIT — no el objeto Empresa completo."""
    p = Producto(
        codigo="PROD-001", nombre="X", caracteristicas="",
        precio_base=_precio_cop(), empresa_nit="830514226-6",
    )
    assert isinstance(p.empresa_nit, str)
    assert not hasattr(p, "empresa")


def test_precio_se_puede_convertir_desde_producto():
    p = Producto(
        codigo="PROD-001", nombre="X", caracteristicas="",
        precio_base=Precio(monto=Decimal("4167"), moneda="COP"),
        empresa_nit="830514226-6",
    )
    precio_usd = p.precio_base.convertir(Decimal("0.000240"), "USD")
    assert precio_usd.moneda == "USD"
    assert precio_usd.monto > Decimal("0")
