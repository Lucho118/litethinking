from rest_framework.permissions import BasePermission

_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def _es_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and user.groups.filter(name="Administrador").exists()
    )


class EsAdministrador(BasePermission):
    """
    Permite el acceso SOLO a usuarios del grupo Administrador.
    Usar cuando ninguna operación (ni lectura) debe ser pública.
    """

    message = "Se requiere rol Administrador."

    def has_permission(self, request, view) -> bool:
        return _es_admin(request.user)


class EsAdministradorOSoloLectura(BasePermission):
    """
    GET / HEAD / OPTIONS → acceso libre, incluso sin autenticar.
    POST / PUT / PATCH / DELETE → solo grupo Administrador.

    Aplicar a nivel de clase en los ViewSets/APIViews de Empresa y Producto.
    """

    message = "Se requiere rol Administrador para operaciones de escritura."

    def has_permission(self, request, view) -> bool:
        if request.method in _SAFE_METHODS:
            return True
        return _es_admin(request.user)
