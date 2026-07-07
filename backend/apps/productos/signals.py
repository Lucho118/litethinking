"""
Signal que vectoriza automáticamente un producto al crearlo o editarlo.

Estrategia:
- Al CREAR un producto (created=True), el embedding es NULL por defecto,
  por lo que el endpoint /agente/reindexar lo procesará.
- Al EDITAR un producto (created=False), reseteamos el embedding a NULL
  para que el reindexador lo vuelva a procesar con el texto actualizado.
- La llamada HTTP al microservicio corre en un hilo separado para no
  bloquear la respuesta de la API de Django.
- Si el microservicio no está disponible, se registra un warning y continúa.
  La vectorización se puede recuperar corriendo manualmente el script.
"""

import logging
import threading

from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _reset_embedding(codigo: str) -> None:
    """Resetea el embedding de un producto a NULL para forzar re-vectorización."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE productos SET embedding = NULL WHERE codigo = %s",
                [codigo],
            )
    except Exception as exc:
        logger.warning("No se pudo resetear embedding de %s: %s", codigo, exc)


def _llamar_reindexar() -> None:
    """Llama al endpoint POST /agente/reindexar del microservicio (fire-and-forget)."""
    try:
        import urllib.request
        import urllib.error
        from django.conf import settings

        url = f"{getattr(settings, 'AI_AGENT_URL', 'http://localhost:8001')}/agente/reindexar"
        req = urllib.request.Request(url, data=b"", method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=90) as resp:
            logger.info("Vectorización completada: %s", resp.read().decode())
    except Exception as exc:
        logger.warning(
            "No se pudo vectorizar automáticamente (¿microservicio inactivo?): %s", exc
        )


def _vectorizar_en_hilo(codigo: str, created: bool) -> None:
    """Resetea embedding si es edición, luego llama al reindexador."""
    if not created:
        _reset_embedding(codigo)
    _llamar_reindexar()


def conectar_signal_vectorizacion():
    """Conecta el signal. Llamado desde ProductosConfig.ready()."""
    from apps.productos.models import ProductoModel

    @receiver(post_save, sender=ProductoModel, dispatch_uid="vectorizar_producto")
    def vectorizar_producto(sender, instance, created, **kwargs):
        hilo = threading.Thread(
            target=_vectorizar_en_hilo,
            args=(instance.codigo, created),
            daemon=True,
        )
        hilo.start()
