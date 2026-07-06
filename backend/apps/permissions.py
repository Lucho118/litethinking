# Re-exporta desde apps.authentication.permissions para compatibilidad.
# Importar directamente desde apps.authentication.permissions en código nuevo.
from apps.authentication.permissions import EsAdministrador, EsAdministradorOSoloLectura  # noqa: F401
