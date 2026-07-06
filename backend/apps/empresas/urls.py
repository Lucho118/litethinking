from django.urls import path
from .views import EmpresaDetailView, EmpresaListCreateView

urlpatterns = [
    path("", EmpresaListCreateView.as_view(), name="empresa-list-create"),
    path("<str:nit>/", EmpresaDetailView.as_view(), name="empresa-detail"),
]
