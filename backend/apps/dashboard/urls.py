from django.urls import path

from .views import DashboardResumenView

urlpatterns = [
    path("resumen/", DashboardResumenView.as_view(), name="dashboard-resumen"),
]
