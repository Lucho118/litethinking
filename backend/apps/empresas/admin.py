from django.contrib import admin

from .models import EmpresaModel


@admin.register(EmpresaModel)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nit", "nombre", "direccion", "telefono")
    search_fields = ("nit", "nombre")
    ordering = ("nombre",)
