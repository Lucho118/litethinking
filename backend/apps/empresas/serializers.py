import re
from rest_framework import serializers

_NIT_PATTERN = re.compile(r"^\d{7,10}-\d$")


class EmpresaSerializer(serializers.Serializer):
    nit = serializers.CharField(max_length=20)
    nombre = serializers.CharField(max_length=255)
    direccion = serializers.CharField(max_length=500)
    telefono = serializers.CharField(max_length=20)

    def validate_nit(self, value: str) -> str:
        if not _NIT_PATTERN.match(value):
            raise serializers.ValidationError(
                "NIT inválido. Formato esperado: dígitos-dígito_verificador (ej. 830514226-6)."
            )
        return value

    def validate_nombre(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value
