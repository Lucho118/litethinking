# test.py ya no sobreescribe DATABASES.
# Los tests usan la misma BD que el servidor de desarrollo:
#   - DATABASE_URL definida en .env → PostgreSQL (u otra BD configurada)
#   - DATABASE_URL ausente           → SQLite (fallback automático en base.py)
from .dev import *  # noqa: F401, F403
