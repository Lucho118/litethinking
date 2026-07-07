from .base import *  # noqa: F401, F403

# En producción todos los valores deben venir de variables de entorno.
# No se usa archivo .env en el servidor.
DEBUG = True

# ALLOWED_HOSTS viene de la variable de entorno leída en base.py (django-environ).
# No hace falta sobreescribir aquí — base.py ya la parsea como lista.

# ── HTTPS / seguridad ────────────────────────────────────────────────────────
# Render termina SSL en su proxy — confiar en el header X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Logging: enviar errores e info de Django a stdout (visible en Render → Logs)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "apps.productos.signals": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
