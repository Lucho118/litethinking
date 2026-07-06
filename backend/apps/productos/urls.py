from django.urls import path

from .views import ProductoDetailView, ProductoListCreateView, ProductoPorEmpresaView

urlpatterns = [
    # Específicos antes del catch-all <str:codigo>/
    path("por-empresa/<str:nit>/", ProductoPorEmpresaView.as_view(), name="producto-por-empresa"),
    path("", ProductoListCreateView.as_view(), name="producto-list-create"),
    path("<str:codigo>/", ProductoDetailView.as_view(), name="producto-detail"),
]
