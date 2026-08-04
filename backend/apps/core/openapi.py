from functools import cache
from typing import Any

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers, status

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


def add_internal_server_error_response(
    result: dict[str, Any],
    **_: Any,
) -> dict[str, Any]:
    methods = {
        'get',
        'post',
        'put',
        'patch',
        'delete',
    }

    for path_item in result.get(
        'paths',
        {},
    ).values():
        for method, operation in path_item.items():
            if method not in methods:
                continue

            operation.setdefault(
                'responses',
                {},
            ).setdefault(
                str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                {
                    'description': ('Error interno del servidor.'),
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': ('#/components/schemas/ApiErrorResponse'),
                            },
                        },
                    },
                },
            )

    return result
