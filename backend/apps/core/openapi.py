from functools import cache

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .serializers import ApiMetaSerializer


@cache
def success_response_schema(
    *,
    component_name: str,
    data_serializer: type[serializers.Serializer],
) -> type[serializers.Serializer]:
    @extend_schema_serializer(
        many=False,
        component_name=component_name,
    )
    class SuccessResponseSerializer(serializers.Serializer):
        data = data_serializer()
        meta = ApiMetaSerializer()

    return SuccessResponseSerializer
