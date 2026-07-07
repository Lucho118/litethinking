import environ
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lee .env si existe — si no existe usa solo variables de entorno del sistema
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file)

# ── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local apps
    "apps.authentication",
    "apps.empresas",
    "apps.productos",
    "apps.auditoria",
    "apps.dashboard",
]

# ── Middleware ────────────────────────────────────────────────────────────────
# CorsMiddleware must come before CommonMiddleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
# Si DATABASE_URL está definida (en .env o en el entorno del sistema) → usa esa BD.
# Si no está definida → SQLite automáticamente (desarrollo sin PostgreSQL).
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},    # Custom: exige mayúscula, dígito y carácter especial
    {"NAME": "apps.authentication.validators.FuertePasswordValidator"},]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Permiso por defecto: solo lectura para todos; las vistas de escritura
    # declaran EsAdministradorOSoloLectura explícitamente.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000"],
)

# URL del microservicio AI (FastAPI). Se usa en signals de vectorización.
AI_AGENT_URL = env.str("AI_AGENT_URL", default="http://localhost:8001")

# ── Email (Gmail SMTP) ────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST     = env.str("EMAIL_HOST",      default="smtp.gmail.com")
EMAIL_PORT     = env.int("EMAIL_PORT",      default=465)
EMAIL_USE_TLS  = env.bool("EMAIL_USE_TLS",  default=False)
EMAIL_USE_SSL  = env.bool("EMAIL_USE_SSL",  default=True)
EMAIL_TIMEOUT  = 10  # segundos — evita que la conexión SMTP bloquee el worker
EMAIL_HOST_USER     = env.str("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = env.str("DEFAULT_FROM_EMAIL",  default="noreply@litethinking.com")

# ── Authentication backend ─────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    # Autentica con email en lugar de username (véase apps/authentication/backends.py)
    "apps.authentication.backends.EmailBackend",
]

# ── JWT (djangorestframework-simplejwt) ──────────────────────────────────────
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    # Tiempos de expiración — ajustar en prodón según política de seguridad
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}