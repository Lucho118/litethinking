from __future__ import annotations

from apps.auditoria.repositories import AuditoriaRepository
from apps.empresas.repositories import EmpresaRepository
from apps.productos.repositories import ConsultaProductoRepository, ProductoRepository


class ObtenerResumenDashboardUseCase:
    """
    Agrega métricas del sistema para el Dashboard de Administrador.

    Sigue el mismo patrón que el resto del backend:
    la vista no toca el ORM directamente — todo pasa por repositorios.
    """

    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        producto_repo: ProductoRepository,
        auditoria_repo: AuditoriaRepository,
        consulta_repo: ConsultaProductoRepository,
    ) -> None:
        self._empresa_repo = empresa_repo
        self._producto_repo = producto_repo
        self._auditoria_repo = auditoria_repo
        self._consulta_repo = consulta_repo

    def ejecutar(self) -> dict:
        producto_top = self._consulta_repo.producto_mas_consultado()

        return {
            "total_empresas": self._empresa_repo.contar(),
            "total_productos": self._producto_repo.contar(),
            "top_5_empresas": self._empresa_repo.top_5_con_mas_productos(),
            "producto_mas_consultado": (
                {
                    "codigo": producto_top.codigo,
                    "nombre": producto_top.nombre,
                    "total_consultas": producto_top.total_consultas,
                }
                if producto_top
                else None  # TODO: se puebla después de la primera consulta al agente IA
            ),
            "distribucion_precios": self._producto_repo.distribucion_por_precio(),
            "total_auditoria": self._auditoria_repo.contar_total(),
        }
