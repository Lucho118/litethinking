from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.permissions import EsAdministrador

from .repositories import AuditoriaRepository
from .serializers import BloqueAuditoriaSerializer


class _AuditoriaPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class AuditoriaListView(APIView):
    """
    GET /api/auditoria/
    Lista completa de la cadena, paginada.  Solo Administrador.
    """

    permission_classes = [EsAdministrador]

    def get(self, request: Request) -> Response:
        bloques = AuditoriaRepository().obtener_cadena_completa()
        paginator = _AuditoriaPagination()
        page = paginator.paginate_queryset(bloques, request)
        data = BloqueAuditoriaSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


class VerificarIntegridadView(APIView):
    """
    GET /api/auditoria/verificar/
    Recorre toda la cadena y devuelve si está íntegra o en qué índice se rompió.
    Solo Administrador.
    """

    permission_classes = [EsAdministrador]

    def get(self, request: Request) -> Response:
        resultado = AuditoriaRepository().verificar_integridad()
        http_status = (
            status.HTTP_200_OK if resultado["integra"] else status.HTTP_409_CONFLICT
        )
        return Response(resultado, status=http_status)


class AuditoriaEntidadView(APIView):
    """
    GET /api/auditoria/entidad/<entidad>/<entidad_id>/
    Historial de cambios de una empresa o producto específico.
    Solo Administrador.
    """

    permission_classes = [EsAdministrador]

    def get(self, request: Request, entidad: str, entidad_id: str) -> Response:
        bloques = AuditoriaRepository().obtener_por_entidad(entidad, entidad_id)
        return Response(BloqueAuditoriaSerializer(bloques, many=True).data)
