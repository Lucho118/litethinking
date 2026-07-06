from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # App routes will be registered here as apps are added
    # e.g. path("api/v1/companies/", include("apps.companies.urls")),
]
