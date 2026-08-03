from rest_framework import serializers


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()
