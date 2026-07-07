from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from apps.authentication.permissions import EsAdministradorOSoloLectura
from apps.productos.repositories import ProductoRepository, TasaCambioRepository
from apps.productos.serializers import ProductoReadSerializer
from apps.productos.use_cases import ListarProductosUseCase

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
    GET  /api/empresas/  → público
    POST /api/empresas/  → solo Administrador
    """

    permission_classes = [EsAdministradorOSoloLectura]

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

    permission_classes = [EsAdministradorOSoloLectura]

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
        from django.db.models import ProtectedError
        use_case = EliminarEmpresaUseCase(EmpresaRepository())
        try:
            use_case.ejecutar(nit)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError:
            return Response(
                {"error": "No se puede eliminar la empresa porque tiene productos asociados. Elimina primero los productos."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class InventarioView(APIView):
    """
    GET /api/empresas/<nit>/inventario/

    Devuelve los datos de la empresa más la lista completa de sus productos
    con precios en todas las monedas soportadas (COP, USD, EUR).
    Endpoint de solo lectura: accesible para cualquier usuario (incluso sin
    autenticar), consistente con el resto de endpoints GET.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, nit: str) -> Response:
        empresa = ObtenerEmpresaUseCase(EmpresaRepository()).ejecutar(nit)
        if empresa is None:
            return Response(
                {"error": f"No existe ninguna empresa con NIT '{nit}'."},
                status=status.HTTP_404_NOT_FOUND,
            )

        productos_con_precios = ListarProductosUseCase(
            ProductoRepository(), TasaCambioRepository()
        ).ejecutar(empresa_nit=nit)

        return Response(
            {
                "empresa": {
                    "nit": empresa.nit,
                    "nombre": empresa.nombre,
                    "direccion": empresa.direccion,
                    "telefono": empresa.telefono,
                },
                "total_productos": len(productos_con_precios),
                "productos": ProductoReadSerializer(productos_con_precios, many=True).data,
            }
        )


def _obtener_empresa_y_productos(nit: str):
    """Helper compartido por PDF y Email para evitar duplicar la lógica."""
    empresa = ObtenerEmpresaUseCase(EmpresaRepository()).ejecutar(nit)
    if empresa is None:
        return None, None
    productos = ListarProductosUseCase(
        ProductoRepository(), TasaCambioRepository()
    ).ejecutar(empresa_nit=nit)
    return empresa, productos


class InventarioPDFView(APIView):
    """
    GET /api/empresas/<nit>/inventario/pdf/
    Descarga el inventario de la empresa como PDF.
    Requiere autenticación (Bearer token).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, nit: str) -> HttpResponse:
        from .pdf import generar_pdf_inventario

        empresa, productos = _obtener_empresa_y_productos(nit)
        if empresa is None:
            return HttpResponse(
                b'{"error": "Empresa no encontrada."}',
                status=404,
                content_type="application/json",
            )

        pdf_bytes = generar_pdf_inventario(empresa, productos)
        nombre_archivo = f"inventario_{nit.replace('-', '_')}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
        return response


class InventarioEmailView(APIView):
    """
    POST /api/empresas/<nit>/inventario/email/
    Body: { "email": "destinatario@ejemplo.com" }
    Envía el inventario como PDF adjunto al correo indicado.
    Requiere autenticación (Bearer token).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, nit: str) -> Response:
        from django.core.mail import EmailMessage
        from django.conf import settings as django_settings
        from .pdf import generar_pdf_inventario

        email_destino = (request.data or {}).get("email", "").strip()
        if not email_destino:
            return Response(
                {"error": "Se requiere el campo 'email'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        empresa, productos = _obtener_empresa_y_productos(nit)
        if empresa is None:
            return Response(
                {"error": "Empresa no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        pdf_bytes = generar_pdf_inventario(empresa, productos)
        nombre_archivo = f"inventario_{nit.replace('-', '_')}.pdf"

        msg = EmailMessage(
            subject=f"Inventario de productos — {empresa.nombre}",
            body=(
                f"Estimado/a,\n\n"
                f"Adjunto encontrará el inventario actualizado de {empresa.nombre} "
                f"(NIT: {empresa.nit}).\n\n"
                f"Total de productos: {len(productos)}\n\n"
                f"Saludos,\nLiteThinking"
            ),
            from_email=getattr(django_settings, "DEFAULT_FROM_EMAIL", "noreply@litethinking.com"),
            to=[email_destino],
        )
        msg.attach(nombre_archivo, pdf_bytes, "application/pdf")

        try:
            msg.send()
        except Exception as exc:
            return Response(
                {"error": f"No se pudo enviar el correo: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"mensaje": f"Inventario enviado a {email_destino}."},
            status=status.HTTP_200_OK,
        )
