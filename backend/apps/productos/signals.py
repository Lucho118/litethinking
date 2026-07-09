"""
Signal que vectoriza automáticamente un producto al crearlo o editarlo.

Estrategia:
- Función definida a nivel de módulo (no closure) para que Python mantenga
  una referencia fuerte y no haga garbage collect del handler con weak=True.
- Se conecta mediante 'import apps.productos.signals' en ProductosConfig.ready().
- transaction.on_commit garantiza que el hilo arranca DESPUÉS del commit
  (update_or_create usa transaction.atomic() internamente).
- Si el microservicio no está disponible, se registra el error y continúa.
"""

import sys
import threading

from django.db import connection, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


def _reset_embedding(codigo: str) -> None:
    """Resetea el embedding de un producto a NULL para forzar re-vectorización."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE productos SET embedding = NULL WHERE codigo = %s",
                [codigo],
            )
    except Exception as exc:
        print(f"[signal] WARNING: No se pudo resetear embedding de '{codigo}': {exc}", file=sys.stderr, flush=True)


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


# ── Signal handler a nivel de módulo ─────────────────────────────────────────
# Definido aquí (NO dentro de una función) para que el módulo mantenga una
# referencia fuerte. Con weak=True (default Django), los closures locales
# pueden ser recolectados por el GC después de que conectar_signal_vectorizacion()
# retorna, dejando el signal registrado pero con referencia muerta.
# Se usa la cadena 'app_label.ModelName' como sender para evitar importar
# ProductoModel aquí y causar circular imports al cargar el módulo.
@receiver(post_save, sender="productos.ProductoModel", dispatch_uid="vectorizar_producto")
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
