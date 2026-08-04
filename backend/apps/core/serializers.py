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


class ProblemDetailSerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    status = serializers.IntegerField()
    detail = serializers.CharField()
    instance = serializers.CharField(allow_null=True)
    errors = serializers.JSONField(required=False)


class ApiErrorResponseSerializer(serializers.Serializer):
    error = ProblemDetailSerializer()
    meta = ApiMetaSerializer()


class HealthResponseSerializer(serializers.Serializer):
    data = HealthDataSerializer()
    meta = ResponseMetaSerializer()
