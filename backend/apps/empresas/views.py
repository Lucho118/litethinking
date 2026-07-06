from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.permissions import EsAdministrador

from .repositories import EmpresaRepository
from .serializers import EmpresaSerializer
from .use_cases import (
    ActualizarEmpresaUseCase,
    CrearEmpresaUseCase,
    EliminarEmpresaUseCase,
    ListarEmpresasUseCase,
    ObtenerEmpresaUseCase,
)


# ── Views ─────────────────────────────────────────────────────────────────────

class EmpresaListCreateView(APIView):
    """
    GET  /api/empresas/  → público (AllowAny)
    POST /api/empresas/  → solo grupo Administrador
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsAdministrador()]

    def get(self, request: Request) -> Response:
        use_case = ListarEmpresasUseCase(EmpresaRepository())
        empresas = use_case.ejecutar()
        return Response(EmpresaSerializer(empresas, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = EmpresaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        use_case = CrearEmpresaUseCase(EmpresaRepository())
        try:
            empresa = use_case.ejecutar(**serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(EmpresaSerializer(empresa).data, status=status.HTTP_201_CREATED)


class EmpresaDetailView(APIView):
    """
    GET    /api/empresas/<nit>/  → público (AllowAny)
    PUT    /api/empresas/<nit>/  → solo grupo Administrador
    DELETE /api/empresas/<nit>/  → solo grupo Administrador
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsAdministrador()]

    def get(self, request: Request, nit: str) -> Response:
        empresa = ObtenerEmpresaUseCase(EmpresaRepository()).ejecutar(nit)
        if empresa is None:
            return Response({"error": "Empresa no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmpresaSerializer(empresa).data)

    def put(self, request: Request, nit: str) -> Response:
        # NIT comes from the URL; body provides the rest of the fields
        data = {**request.data, "nit": nit}
        serializer = EmpresaSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        use_case = ActualizarEmpresaUseCase(EmpresaRepository())
        try:
            empresa = use_case.ejecutar(**serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(EmpresaSerializer(empresa).data)

    def delete(self, request: Request, nit: str) -> Response:
        use_case = EliminarEmpresaUseCase(EmpresaRepository())
        try:
            use_case.ejecutar(nit)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
