import logging

from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler

from .context import get_request_id
from .error_payload import build_error_payload

logger = logging.getLogger(__name__)


class ConflictError(drf_exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El recurso está en un estado que no permite esta operación.'
    default_code = 'conflict'

_KNOWN_EXCEPTION_MAP = (
    (drf_exceptions.ValidationError, ('VALIDATION_ERROR', status.HTTP_400_BAD_REQUEST)),
    (drf_exceptions.NotAuthenticated, ('NOT_AUTHENTICATED', status.HTTP_401_UNAUTHORIZED)),
    (drf_exceptions.AuthenticationFailed, ('NOT_AUTHENTICATED', status.HTTP_401_UNAUTHORIZED)),
    (drf_exceptions.PermissionDenied, ('PERMISSION_DENIED', status.HTTP_403_FORBIDDEN)),
    (drf_exceptions.NotFound, ('NOT_FOUND', status.HTTP_404_NOT_FOUND)),
    (Http404, ('NOT_FOUND', status.HTTP_404_NOT_FOUND)),
    (ConflictError, ('CONFLICT', status.HTTP_409_CONFLICT)),
)


def _map_known_exception(exc):
    for exc_class, mapping in _KNOWN_EXCEPTION_MAP:
        if isinstance(exc, exc_class):
            return mapping
    default_status = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
    return 'ERROR', default_status


def _build_validation_details(detail) -> list:
    details = []

    def _add(field, message):
        details.append({'field': field, 'message': str(message)})

    if isinstance(detail, dict):
        for field, messages in detail.items():
            if isinstance(messages, (list, tuple)):
                for message in messages:
                    _add(field, message)
            else:
                _add(field, messages)
    elif isinstance(detail, list):
        for item in detail:
            if isinstance(item, dict):
                for field, messages in item.items():
                    if isinstance(messages, (list, tuple)):
                        for message in messages:
                            _add(field, message)
                    else:
                        _add(field, messages)
            else:
                _add('non_field_errors', item)
    elif detail is not None:
        _add('non_field_errors', detail)

    return details


def _extract_message(response_data) -> str:
    if isinstance(response_data, dict) and 'detail' in response_data:
        return str(response_data['detail'])
    if isinstance(response_data, str):
        return response_data
    return 'Ocurrió un error al procesar la solicitud.'


def custom_exception_handler(exc, context):
    request_id = get_request_id()
    response = drf_default_exception_handler(exc, context)

    if response is not None:
        code, status_code = _map_known_exception(exc)

        if isinstance(exc, drf_exceptions.ValidationError):
            details = _build_validation_details(response.data)
            message = 'Uno o más campos no son válidos.'
        else:
            details = []
            message = _extract_message(response.data)

        response.data = build_error_payload(code, message, details)
        response.status_code = status_code
        return response

    logger.exception(
        'Excepción no controlada en una vista de la API',
        extra={'request_id': request_id},
    )
    return Response(
        build_error_payload(
            'INTERNAL_ERROR',
            'Ocurrió un error interno. Intenta nuevamente más tarde.',
        ),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
