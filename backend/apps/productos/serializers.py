from decimal import Decimal

from rest_framework import serializers

from domain.entities.precio import MONEDAS_VALIDAS


class ProductoWriteSerializer(serializers.Serializer):
    """Serializer de entrada para crear o actualizar un producto."""

    codigo = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=255)
    caracteristicas = serializers.CharField(allow_blank=True, default="")
    precio_monto = serializers.DecimalField(
        max_digits=18, decimal_places=2, min_value=Decimal("0")
    )
    precio_moneda = serializers.ChoiceField(
        choices=sorted(MONEDAS_VALIDAS), default="COP"
    )
    cantidad = serializers.IntegerField(min_value=0, default=0)
    empresa_nit = serializers.CharField(max_length=20)

    def validate_codigo(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("El código no puede estar vacío.")
        return value

    def validate_nombre(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value


class ProductoReadSerializer(serializers.Serializer):
    """
    Serializer de salida para un ProductoConPrecios.
    Usa to_representation para mapear explícitamente el dataclass.
    """

    def to_representation(self, instance) -> dict:
        p = instance.detalle.producto
        return {
            "codigo": p.codigo,
            "nombre": p.nombre,
            "caracteristicas": p.caracteristicas,
            "cantidad": p.cantidad,
            "empresa_nit": p.empresa_nit,
            "empresa_nombre": instance.detalle.empresa_nombre,
            "precio_base": {
                "monto": str(p.precio_base.monto),
                "moneda": p.precio_base.moneda,
            },
            "precios": {
                moneda: {"monto": str(precio.monto), "moneda": precio.moneda}
                for moneda, precio in sorted(instance.precios.items())
            },
        }
