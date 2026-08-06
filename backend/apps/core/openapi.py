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


def add_standard_error_responses(
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
    error_responses = {
        str(
            status.HTTP_429_TOO_MANY_REQUESTS,
        ): 'Límite de solicitudes excedido.',
        str(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ): 'Error interno del servidor.',
    }
    mutation_error_responses = {
        str(
            status.HTTP_409_CONFLICT,
        ): 'La operación entra en conflicto con el estado actual de los datos.',
    }

    for path_item in result.get(
        'paths',
        {},
    ).values():
        for method, operation in path_item.items():
            if method not in methods:
                continue

            responses = operation.setdefault(
                'responses',
                {},
            )

            applicable_error_responses = dict(error_responses)

            if method in {
                'post',
                'put',
                'patch',
                'delete',
            }:
                applicable_error_responses.update(
                    mutation_error_responses,
                )

            for status_code, description in applicable_error_responses.items():
                responses.setdefault(
                    status_code,
                    {
                        'description': description,
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
