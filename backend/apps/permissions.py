from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class EsAdministrador(BasePermission):
    """
    Permite el acceso solo a usuarios autenticados que pertenecen al
    grupo 'Administrador'.  Usar en operaciones de escritura (POST, PUT, DELETE).
    GET queda como AllowAny en cada vista.
    """

    message = "Solo usuarios del grupo Administrador pueden realizar esta acción."

    def has_permission(self, request: Request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="Administrador").exists()
        )
