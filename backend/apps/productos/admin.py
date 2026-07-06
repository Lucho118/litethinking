from django.contrib import admin

from .models import ProductoModel, TasaCambioModel


@admin.register(ProductoModel)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio_base", "moneda_base", "empresa")
    list_filter = ("moneda_base", "empresa")
    search_fields = ("codigo", "nombre")
    ordering = ("nombre",)


@admin.register(TasaCambioModel)
class TasaCambioAdmin(admin.ModelAdmin):
    list_display = ("moneda_origen", "moneda_destino", "tasa", "fecha_actualizacion")
    ordering = ("moneda_origen", "moneda_destino")
