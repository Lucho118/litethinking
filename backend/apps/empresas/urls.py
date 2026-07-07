from django.urls import path
from .views import (
    EmpresaDetailView,
    EmpresaListCreateView,
    InventarioView,
    InventarioPDFView,
    InventarioEmailView,
)

urlpatterns = [
    path("", EmpresaListCreateView.as_view(), name="empresa-list-create"),
    # Rutas específicas antes de <str:nit>/ para evitar ambigüedad
    path("<str:nit>/inventario/", InventarioView.as_view(), name="empresa-inventario"),
    path("<str:nit>/inventario/pdf/", InventarioPDFView.as_view(), name="empresa-inventario-pdf"),
    path("<str:nit>/inventario/email/", InventarioEmailView.as_view(), name="empresa-inventario-email"),
    path("<str:nit>/", EmpresaDetailView.as_view(), name="empresa-detail"),
]
