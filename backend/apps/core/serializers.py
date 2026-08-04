from rest_framework import serializers


class ResponseMetaSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    api_version = serializers.CharField()
    timestamp = serializers.DateTimeField()


class HealthDataSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()


class ApiMetaSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    api_version = serializers.CharField()
    timestamp = serializers.DateTimeField()


class HealthResponseSerializer(serializers.Serializer):
    data = HealthDataSerializer()
    meta = ResponseMetaSerializer()
