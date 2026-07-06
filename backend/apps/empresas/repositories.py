from __future__ import annotations

from domain.entities.empresa import Empresa
from .models import EmpresaModel


class EmpresaRepository:
    """
    Traduce entre EmpresaModel (ORM / infraestructura) y
    Empresa (entidad de dominio).  Ninguna capa superior toca
    EmpresaModel directamente.
    """

    def guardar(self, empresa: Empresa) -> Empresa:
        model, _ = EmpresaModel.objects.update_or_create(
            nit=empresa.nit,
            defaults={
                "nombre": empresa.nombre,
                "direccion": empresa.direccion,
                "telefono": empresa.telefono,
            },
        )
        return self._to_entity(model)

    def obtener(self, nit: str) -> Empresa | None:
        try:
            return self._to_entity(EmpresaModel.objects.get(nit=nit))
        except EmpresaModel.DoesNotExist:
            return None

    def listar(self) -> list[Empresa]:
        return [self._to_entity(m) for m in EmpresaModel.objects.all().order_by("nombre")]

    def eliminar(self, nit: str) -> bool:
        deleted, _ = EmpresaModel.objects.filter(nit=nit).delete()
        return deleted > 0

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: EmpresaModel) -> Empresa:
        return Empresa(
            nit=model.nit,
            nombre=model.nombre,
            direccion=model.direccion,
            telefono=model.telefono,
        )
