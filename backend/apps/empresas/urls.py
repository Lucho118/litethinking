from django.urls import path
from .views import EmpresaDetailView, EmpresaListCreateView, InventarioView

urlpatterns = [
    path("", EmpresaListCreateView.as_view(), name="empresa-list-create"),
    # Inventario antes de <str:nit>/ para evitar ambigüedad
    path("<str:nit>/inventario/", InventarioView.as_view(), name="empresa-inventario"),
    path("<str:nit>/", EmpresaDetailView.as_view(), name="empresa-detail"),
]
