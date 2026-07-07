from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.repositories import AuditoriaRepository
from apps.authentication.permissions import EsAdministrador
from apps.empresas.repositories import EmpresaRepository
from apps.productos.repositories import ConsultaProductoRepository, ProductoRepository

from .use_cases import ObtenerResumenDashboardUseCase


class DashboardResumenView(APIView):
    """
    GET /api/dashboard/resumen/

    Devuelve métricas agregadas del sistema.
    Solo accesible para usuarios del grupo Administrador (403 para Externo).
    """

    permission_classes = [EsAdministrador]

    def get(self, request: Request) -> Response:
        use_case = ObtenerResumenDashboardUseCase(
            empresa_repo=EmpresaRepository(),
            producto_repo=ProductoRepository(),
            auditoria_repo=AuditoriaRepository(),
            consulta_repo=ConsultaProductoRepository(),
        )
        return Response(use_case.ejecutar())
