from django.urls import path

from .views import AuditoriaEntidadView, AuditoriaListView, VerificarIntegridadView

urlpatterns = [
    # Específicos antes del catch-all
    path("verificar/", VerificarIntegridadView.as_view(), name="auditoria-verificar"),
    path("entidad/<str:entidad>/<str:entidad_id>/", AuditoriaEntidadView.as_view(), name="auditoria-entidad"),
    path("", AuditoriaListView.as_view(), name="auditoria-list"),
]
