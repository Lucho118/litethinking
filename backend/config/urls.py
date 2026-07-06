from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/auditoria/", include("apps.auditoria.urls")),
    path("api/empresas/", include("apps.empresas.urls")),
    path("api/productos/", include("apps.productos.urls")),
]
