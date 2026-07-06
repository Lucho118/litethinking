from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.empresas.repositories import EmpresaRepository
from apps.permissions import EsAdministrador

from .repositories import ProductoRepository, TasaCambioRepository
from .serializers import ProductoReadSerializer, ProductoWriteSerializer
from .use_cases import (
    ActualizarProductoUseCase,
    CrearProductoUseCase,
    EliminarProductoUseCase,
    ListarProductosUseCase,
    ObtenerProductoConPreciosUseCase,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _repos():
    return ProductoRepository(), TasaCambioRepository(), EmpresaRepository()


# ── Views ─────────────────────────────────────────────────────────────────────

class ProductoListCreateView(APIView):
    """
    GET  /api/productos/           → público; acepta ?empresa_nit=<nit>
    POST /api/productos/           → solo Administrador
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsAdministrador()]

    def get(self, request: Request) -> Response:
        empresa_nit = request.query_params.get("empresa_nit")
        producto_repo, tasa_repo, _ = _repos()
        productos = ListarProductosUseCase(producto_repo, tasa_repo).ejecutar(empresa_nit)
        return Response(ProductoReadSerializer(productos, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ProductoWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        producto_repo, _, empresa_repo = _repos()
        try:
            CrearProductoUseCase(producto_repo, empresa_repo).ejecutar(
                **serializer.validated_data
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the created product with prices
        _, tasa_repo, _ = _repos()
        resultado = ObtenerProductoConPreciosUseCase(producto_repo, tasa_repo).ejecutar(
            serializer.validated_data["codigo"]
        )
        return Response(ProductoReadSerializer(resultado).data, status=status.HTTP_201_CREATED)


class ProductoDetailView(APIView):
    """
    GET    /api/productos/<codigo>/   → público; acepta ?moneda=USD,EUR
    PUT    /api/productos/<codigo>/   → solo Administrador
    DELETE /api/productos/<codigo>/   → solo Administrador
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [EsAdministrador()]

    def get(self, request: Request, codigo: str) -> Response:
        # Opcional: ?moneda=USD o ?moneda=USD,EUR para limitar monedas devueltas
        monedas_param = request.query_params.get("moneda")
        monedas = [m.strip().upper() for m in monedas_param.split(",")] if monedas_param else None

        producto_repo, tasa_repo, _ = _repos()
        resultado = ObtenerProductoConPreciosUseCase(producto_repo, tasa_repo).ejecutar(
            codigo, monedas
        )
        if resultado is None:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductoReadSerializer(resultado).data)

    def put(self, request: Request, codigo: str) -> Response:
        data = {**request.data, "codigo": codigo}  # NIT/código siempre del URL
        serializer = ProductoWriteSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        producto_repo, tasa_repo, empresa_repo = _repos()
        try:
            ActualizarProductoUseCase(producto_repo, empresa_repo).ejecutar(
                **serializer.validated_data
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        resultado = ObtenerProductoConPreciosUseCase(producto_repo, tasa_repo).ejecutar(codigo)
        return Response(ProductoReadSerializer(resultado).data)

    def delete(self, request: Request, codigo: str) -> Response:
        producto_repo, _, _ = _repos()
        try:
            EliminarProductoUseCase(producto_repo).ejecutar(codigo)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductoPorEmpresaView(APIView):
    """
    GET /api/productos/por-empresa/<nit>/  → público
    Alias explícito del filtro por empresa para el inventario del frontend.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, nit: str) -> Response:
        producto_repo, tasa_repo, _ = _repos()
        productos = ListarProductosUseCase(producto_repo, tasa_repo).ejecutar(empresa_nit=nit)
        return Response(ProductoReadSerializer(productos, many=True).data)
