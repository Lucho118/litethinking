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
import sys
import threading

from django.db import connection, transaction
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


def _llamar_reindexar(codigo: str) -> None:
    """Vectoriza un producto específico e invalida el cache del agente."""
    try:
        import urllib.request
        from django.conf import settings

        base_url = getattr(settings, 'AI_AGENT_URL', 'http://localhost:8001')
        url = f"{base_url}/agente/reindexar/{codigo}"
        print(f"[signal] Llamando microservicio: POST {url}", file=sys.stderr, flush=True)
        req = urllib.request.Request(url, data=b"", method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read()
            print(f"[signal] Vectorización exitosa para '{codigo}': {body.decode()}", file=sys.stderr, flush=True)
    except Exception as exc:
        print(f"[signal] ERROR al vectorizar '{codigo}': {exc}", file=sys.stderr, flush=True)


def _vectorizar_en_hilo(codigo: str, created: bool) -> None:
    """Resetea embedding si es edición, luego vectoriza solo ese producto."""
    if not created:
        _reset_embedding(codigo)
    _llamar_reindexar(codigo)


def conectar_signal_vectorizacion():
    """Conecta el signal. Llamado desde ProductosConfig.ready()."""
    from apps.productos.models import ProductoModel

    @receiver(post_save, sender=ProductoModel, dispatch_uid="vectorizar_producto")
    def vectorizar_producto(sender, instance, created, **kwargs):
        codigo = instance.codigo
        print(f"[signal] post_save recibido para '{codigo}' (created={created})", file=sys.stderr, flush=True)

        def iniciar_hilo():
            print(f"[signal] on_commit ejecutado para '{codigo}' — arrancando hilo", file=sys.stderr, flush=True)
            hilo = threading.Thread(
                target=_vectorizar_en_hilo,
                args=(codigo, created),
                daemon=False,
            )
            hilo.start()

        transaction.on_commit(iniciar_hilo)
