from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime

# Hash convencional del bloque génesis (sin predecesor).
# 64 ceros = longitud estándar de SHA-256 en hex.
HASH_GENESIS: str = "0" * 64


@dataclass
class BloqueAuditoria:
    """
    Representa un bloque en la cadena de auditoría inmutable.

    Cada bloque contiene el hash del bloque anterior, lo que permite
    detectar cualquier manipulación posterior a la creación del registro
    (el mismo principio fundamental de Blockchain).

    hash_actual se calcula automáticamente en __post_init__ si se deja vacío.
    Al cargar desde BD se pasa el hash ya almacenado para no recalcularlo.
    """

    indice: int
    timestamp: datetime
    entidad: str        # "Empresa" | "Producto"
    entidad_id: str     # NIT o código del producto
    accion: str         # "CREAR" | "EDITAR" | "ELIMINAR"
    datos: dict
    hash_anterior: str  # HASH_GENESIS para el primer bloque
    hash_actual: str = field(default="")  # vacío → se calcula en __post_init__

    def __post_init__(self) -> None:
        if not self.hash_actual:
            self.hash_actual = self.calcular_hash()

    # ── Core methods ──────────────────────────────────────────────────────────

    def calcular_hash(self) -> str:
        """
        SHA-256 sobre el contenido completo del bloque.
        sort_keys=True garantiza determinismo independientemente del orden
        de inserción de claves en el dict de datos.
        default=str maneja Decimal y otros tipos no serializables.
        """
        contenido = json.dumps(
            {
                "indice": self.indice,
                "timestamp": self.timestamp.isoformat(),
                "entidad": self.entidad,
                "entidad_id": self.entidad_id,
                "accion": self.accion,
                "datos": self.datos,
                "hash_anterior": self.hash_anterior,
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def es_integro(self) -> bool:
        """
        Verifica que el hash almacenado coincide con el recalculado.
        Un bloque no íntegro indica que sus datos fueron alterados en BD.
        """
        return self.calcular_hash() == self.hash_actual

    def es_valido(self, bloque_anterior: "BloqueAuditoria | None") -> bool:
        """
        Regla de negocio de la cadena — dos condiciones deben cumplirse:
        1. El bloque no fue alterado (hash_actual correcto).
        2. La cadena está conectada: hash_anterior == hash_actual del previo
           (o HASH_GENESIS para el primer bloque).
        """
        if not self.es_integro():
            return False
        if bloque_anterior is None:
            return self.hash_anterior == HASH_GENESIS
        return self.hash_anterior == bloque_anterior.hash_actual
