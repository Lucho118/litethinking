from __future__ import annotations

from dataclasses import dataclass

from .precio import Precio


@dataclass
class Producto:
    codigo: str
    nombre: str
    caracteristicas: str
    precio_base: Precio
    empresa_nit: str  # solo el identificador — NO el objeto Empresa completo
    cantidad: int = 0

    def __post_init__(self) -> None:
        self._validar_codigo()
        self._validar_nombre()
        self._validar_cantidad()

    # ── Domain rules ──────────────────────────────────────────────────────────

    def _validar_codigo(self) -> None:
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código del producto no puede estar vacío.")

    def _validar_nombre(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")

    def _validar_cantidad(self) -> None:
        if self.cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
