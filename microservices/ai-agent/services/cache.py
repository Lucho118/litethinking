"""
Cache en memoria para respuestas del agente IA.

Estrategia:
  - TTLCache de cachetools: elimina entradas automáticamente al expirar.
  - Key: SHA-256 de la pregunta normalizada (lowercase + strip) para capturar
    variantes de formato (espacios extra, mayúsculas) de la misma consulta.
  - Lock de threading para que FastAPI en modo multi-worker no tenga race conditions.
  - TTL de 1 hora: balance entre costo OpenAI y frescura del catálogo.

Por qué cachetools sobre Redis:
  - No requiere infraestructura extra (adecuado para una prueba técnica).
  - Para producción, reemplazar esta clase por una que use Redis es trivial.
"""
from __future__ import annotations

import hashlib
import threading
from typing import Any, Optional

from cachetools import TTLCache

_TTL_SEGUNDOS = 3600  # 1 hora
_CAPACIDAD_MAX = 256  # entradas máximas en memoria


class RespuestaCache:
    """Wrapper thread-safe sobre TTLCache para respuestas del agente."""

    def __init__(self, maxsize: int = _CAPACIDAD_MAX, ttl: int = _TTL_SEGUNDOS) -> None:
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.Lock()

    @staticmethod
    def normalizar_key(pregunta: str) -> str:
        """Convierte la pregunta a una clave normalizada y la hashea."""
        normalizada = pregunta.strip().lower()
        return hashlib.sha256(normalizada.encode("utf-8")).hexdigest()

    def obtener(self, pregunta: str) -> Optional[Any]:
        key = self.normalizar_key(pregunta)
        with self._lock:
            return self._cache.get(key)

    def guardar(self, pregunta: str, valor: Any) -> None:
        key = self.normalizar_key(pregunta)
        with self._lock:
            self._cache[key] = valor

    def invalidad_todo(self) -> None:
        """Vacía el cache — útil en tests."""
        with self._lock:
            self._cache.clear()


# Instancia singleton — compartida por todos los requests del proceso
respuesta_cache = RespuestaCache()
