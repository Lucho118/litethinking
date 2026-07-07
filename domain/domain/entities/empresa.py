from __future__ import annotations
import re
from dataclasses import dataclass

# Regex for Colombian NIT: 7-10 digits, hyphen, 1 verification digit
# Examples: 830514226-6  /  9001234567-1
_NIT_PATTERN = re.compile(r"^\d{7,10}-\d$")


@dataclass
class Empresa:
    """
    Entidad de dominio que representa una empresa registrada en el sistema.

    Reglas de negocio:
    - El NIT debe seguir el formato colombiano: 7-10 dígitos, guión, 1 dígito verificador.
    - El nombre no puede estar vacío.

    Esta clase no tiene dependencias de framework — es Python puro.
    Los modelos ORM y serializers viven en backend/, no aquí.
    """
    nit: str
    nombre: str
    direccion: str
    telefono: str

    def __post_init__(self) -> None:
        self._validar_nit()
        self._validar_nombre()

    # ── Domain rules ──────────────────────────────────────────────────────────

    def _validar_nit(self) -> None:
        if not _NIT_PATTERN.match(self.nit):
            raise ValueError(
                f"NIT inválido: {self.nit!r}. "
                "El formato debe ser dígitos-dígito_verificador (ej. 830514226-6)."
            )

    def _validar_nombre(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la empresa no puede estar vacío.")
