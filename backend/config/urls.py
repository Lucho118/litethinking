from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"status": "ok"}, status=200)

urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/auditoria/", include("apps.auditoria.urls")),
    path("api/empresas/", include("apps.empresas.urls")),
    path("api/productos/", include("apps.productos.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
]
