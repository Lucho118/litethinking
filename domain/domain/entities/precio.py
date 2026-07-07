from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# Monedas soportadas (ISO 4217).
# En producción este conjunto se ampliaría desde configuración, no hardcodeado aquí.
MONEDAS_VALIDAS: frozenset[str] = frozenset({"COP", "USD", "EUR"})


@dataclass(frozen=True)  # immutable — Precio es un value object
class Precio:
    """
    Value object que representa un monto de dinero en una moneda específica.

    Es inmutable (frozen=True): una vez creado, no se puede cambiar.
    Para "modificar" un precio se crea un nuevo objeto Precio.

    Reglas de negocio:
    - El monto no puede ser negativo.
    - La moneda debe ser una de las monedas válidas (COP, USD, EUR).

    El método convertir() aplica una tasa de cambio y devuelve un nuevo Precio
    en la moneda destino, redondeado a 2 decimales (ROUND_HALF_UP).
    """
    monto: Decimal
    moneda: str  # ISO 4217

    def __post_init__(self) -> None:
        if self.monto < Decimal("0"):
            raise ValueError(f"El monto no puede ser negativo: {self.monto}.")
        if self.moneda not in MONEDAS_VALIDAS:
            raise ValueError(
                f"Moneda no soportada: {self.moneda!r}. "
                f"Válidas: {sorted(MONEDAS_VALIDAS)}."
            )

    def convertir(self, tasa: Decimal, moneda_destino: str) -> "Precio":
        """
        Devuelve un nuevo Precio en moneda_destino aplicando la tasa dada.
        La tasa es el multiplicador: precio_destino = precio_origen * tasa.
        """
        if tasa <= Decimal("0"):
            raise ValueError("La tasa de cambio debe ser un valor positivo.")
        monto_convertido = (self.monto * tasa).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return Precio(monto=monto_convertido, moneda=moneda_destino)

    def __str__(self) -> str:
        return f"{self.monto:.2f} {self.moneda}"
