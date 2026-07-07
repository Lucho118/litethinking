from .base import *  # noqa: F401, F403
import os

# En producción todos los valores deben venir de variables de entorno.
# No se usa archivo .env en el servidor.
DEBUG = False

# ALLOWED_HOSTS acepta lista separada por comas en la variable de entorno:
# ALLOWED_HOSTS=litethinking-backend.onrender.com,mi-dominio.com
_hosts_env = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _hosts_env.split(",") if h.strip()]

# ── HTTPS / seguridad ────────────────────────────────────────────────────────
# Render termina SSL en su proxy — confiar en el header X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
