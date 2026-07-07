from __future__ import annotations

from datetime import datetime, timezone

from django.db import transaction

from domain.entities.bloque_auditoria import HASH_GENESIS, BloqueAuditoria

from .models import BloqueAuditoriaModel


class AuditoriaRepository:

    # ── Escritura ─────────────────────────────────────────────────────────────

    def guardar_bloque(
        self,
        entidad: str,
        entidad_id: str,
        accion: str,
        datos: dict,
    ) -> BloqueAuditoria:
        """
        Obtiene el último bloque, calcula el nuevo hash encadenado y persiste.
        select_for_update() previene condiciones de carrera en escrituras concurrentes.
        """
        with transaction.atomic():
            ultimo = (
                BloqueAuditoriaModel.objects
                .select_for_update()
                .order_by("-indice")
                .first()
            )

            hash_anterior = ultimo.hash_actual if ultimo else HASH_GENESIS
            nuevo_indice = (ultimo.indice + 1) if ultimo else 0

            bloque = BloqueAuditoria(
                indice=nuevo_indice,
                timestamp=datetime.now(timezone.utc),
                entidad=entidad,
                entidad_id=entidad_id,
                accion=accion,
                datos=datos,
                hash_anterior=hash_anterior,
                # hash_actual vacío → se calcula automáticamente en __post_init__
            )

            BloqueAuditoriaModel.objects.create(
                indice=bloque.indice,
                timestamp=bloque.timestamp,
                entidad=bloque.entidad,
                entidad_id=bloque.entidad_id,
                accion=bloque.accion,
                datos=bloque.datos,
                hash_anterior=bloque.hash_anterior,
                hash_actual=bloque.hash_actual,
            )

            return bloque

    # ── Lectura ───────────────────────────────────────────────────────────────

    def obtener_cadena_completa(self) -> list[BloqueAuditoria]:
        return [self._to_entity(m) for m in BloqueAuditoriaModel.objects.all()]

    def contar_total(self) -> int:
        return BloqueAuditoriaModel.objects.count()

    def obtener_por_entidad(self, entidad: str, entidad_id: str) -> list[BloqueAuditoria]:
        qs = BloqueAuditoriaModel.objects.filter(
            entidad=entidad, entidad_id=entidad_id
        )
        return [self._to_entity(m) for m in qs]

    def verificar_integridad(self) -> dict:
        """
        Recorre la cadena completa verificando que cada bloque:
        1. No fue alterado (hash almacenado == recalculado).
        2. Está correctamente enlazado al bloque anterior.
        Devuelve el índice exacto donde se detectó la primera ruptura.
        """
        bloques = self.obtener_cadena_completa()

        if not bloques:
            return {
                "integra": True,
                "total_bloques": 0,
                "ruptura_en_indice": None,
                "mensaje": "La cadena está vacía.",
            }

        bloque_anterior: BloqueAuditoria | None = None
        for bloque in bloques:
            if not bloque.es_valido(bloque_anterior):
                return {
                    "integra": False,
                    "total_bloques": len(bloques),
                    "ruptura_en_indice": bloque.indice,
                    "mensaje": (
                        f"Ruptura detectada en el bloque {bloque.indice}. "
                        "El registro fue alterado o la cadena está rota."
                    ),
                }
            bloque_anterior = bloque

        return {
            "integra": True,
            "total_bloques": len(bloques),
            "ruptura_en_indice": None,
            "mensaje": "La cadena de auditoría es íntegra.",
        }

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: BloqueAuditoriaModel) -> BloqueAuditoria:
        return BloqueAuditoria(
            indice=model.indice,
            timestamp=model.timestamp,
            entidad=model.entidad,
            entidad_id=model.entidad_id,
            accion=model.accion,
            datos=model.datos,
            hash_anterior=model.hash_anterior,
            hash_actual=model.hash_actual,   # pasa el hash ya guardado
        )
