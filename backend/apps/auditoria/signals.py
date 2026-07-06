"""
Django signals que conectan EmpresaModel y ProductoModel con el log de auditoría.

Decisión: signals en lugar de llamadas explícitas en los use_cases porque:
- La auditoría es una responsabilidad transversal (cross-cutting concern).
- Los use_cases existentes no necesitan saber que existe un sistema de auditoría.
- post_save provee el flag `created` para distinguir CREAR vs EDITAR sin
  necesidad de lógica adicional en los use_cases.
- Si la auditoría falla (excepción), el bloque try/except garantiza que la
  operación original no se revierte — la auditoría no es crítica para el negocio.

CREAR vs EDITAR: post_save(created=True) → CREAR, post_save(created=False) → EDITAR.
ELIMINAR: post_delete siempre → ELIMINAR.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.empresas.models import EmpresaModel
from apps.productos.models import ProductoModel

from .repositories import AuditoriaRepository
from .use_cases import RegistrarAuditoriaUseCase

logger = logging.getLogger(__name__)


def _registrar(entidad: str, entidad_id: str, accion: str, datos: dict) -> None:
    try:
        RegistrarAuditoriaUseCase(AuditoriaRepository()).ejecutar(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            datos=datos,
        )
    except Exception as exc:  # noqa: BLE001
        # La auditoría nunca debe bloquear la operación principal
        logger.error("Error al registrar auditoría [%s %s %s]: %s", accion, entidad, entidad_id, exc)


# ── Empresa ───────────────────────────────────────────────────────────────────

@receiver(post_save, sender=EmpresaModel)
def auditar_empresa_guardada(sender, instance: EmpresaModel, created: bool, **kwargs) -> None:
    _registrar(
        entidad="Empresa",
        entidad_id=instance.nit,
        accion="CREAR" if created else "EDITAR",
        datos={
            "nit": instance.nit,
            "nombre": instance.nombre,
            "direccion": instance.direccion,
            "telefono": instance.telefono,
        },
    )


@receiver(post_delete, sender=EmpresaModel)
def auditar_empresa_eliminada(sender, instance: EmpresaModel, **kwargs) -> None:
    _registrar(
        entidad="Empresa",
        entidad_id=instance.nit,
        accion="ELIMINAR",
        datos={"nit": instance.nit, "nombre": instance.nombre},
    )


# ── Producto ──────────────────────────────────────────────────────────────────

@receiver(post_save, sender=ProductoModel)
def auditar_producto_guardado(sender, instance: ProductoModel, created: bool, **kwargs) -> None:
    _registrar(
        entidad="Producto",
        entidad_id=instance.codigo,
        accion="CREAR" if created else "EDITAR",
        datos={
            "codigo": instance.codigo,
            "nombre": instance.nombre,
            "precio_base": str(instance.precio_base),   # Decimal → str
            "moneda_base": instance.moneda_base,
            "empresa_nit": instance.empresa_id,
        },
    )


@receiver(post_delete, sender=ProductoModel)
def auditar_producto_eliminado(sender, instance: ProductoModel, **kwargs) -> None:
    _registrar(
        entidad="Producto",
        entidad_id=instance.codigo,
        accion="ELIMINAR",
        datos={"codigo": instance.codigo, "nombre": instance.nombre},
    )
