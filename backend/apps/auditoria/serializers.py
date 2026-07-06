from rest_framework import serializers


class BloqueAuditoriaSerializer(serializers.Serializer):
    indice = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    entidad = serializers.CharField()
    entidad_id = serializers.CharField()
    accion = serializers.CharField()
    datos = serializers.JSONField()
    hash_anterior = serializers.CharField()
    hash_actual = serializers.CharField()
