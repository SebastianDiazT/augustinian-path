import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .context import get_request_id

logger = logging.getLogger(__name__)

_CODE_BY_EXCEPTION = {
    drf_exceptions.ValidationError: 'VALIDATION_ERROR',
    drf_exceptions.NotAuthenticated: 'NOT_AUTHENTICATED',
    drf_exceptions.AuthenticationFailed: 'NOT_AUTHENTICATED',
    drf_exceptions.PermissionDenied: 'PERMISSION_DENIED',
    drf_exceptions.NotFound: 'NOT_FOUND',
    drf_exceptions.Throttled: 'THROTTLED',
}


def _code_for(exc) -> str:
    for exc_type, code in _CODE_BY_EXCEPTION.items():
        if isinstance(exc, exc_type):
            return code
    if getattr(exc, 'status_code', None) == status.HTTP_409_CONFLICT:
        return 'CONFLICT'
    return 'ERROR'


def _details_from(exc_detail) -> list[dict]:
    details = []
    if isinstance(exc_detail, dict):
        for field, messages in exc_detail.items():
            messages = messages if isinstance(messages, list) else [messages]
            for message in messages:
                details.append({'field': field, 'message': str(message)})
    elif isinstance(exc_detail, list):
        for message in exc_detail:
            details.append({'field': None, 'message': str(message)})
    elif exc_detail is not None:
        details.append({'field': None, 'message': str(exc_detail)})
    return details


def _message_for(code: str, detail) -> str:
    if code == 'VALIDATION_ERROR':
        return 'Error de validación.'
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return str(detail[0])
    if isinstance(detail, dict) and detail:
        first_value = next(iter(detail.values()))
        first_value = (
            first_value[0] if (isinstance(first_value, list) and first_value) else first_value
        )
        return str(first_value)
    return 'Ocurrió un error procesando la solicitud.'


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = drf_exceptions.PermissionDenied()
    elif isinstance(exc, DjangoValidationError):
        error_payload = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
        exc = drf_exceptions.ValidationError(error_payload)

    response = drf_exception_handler(exc, context)
    request_id = get_request_id()

    if response is not None:
        code = _code_for(exc)
        response.data = {
            'error': {
                'code': code,
                'message': _message_for(code, exc.detail),
                'details': _details_from(exc.detail),
                'request_id': request_id,
            },
        }
        return response

    logger.exception('Unhandled exception', extra={'request_id': request_id})
    return Response(
        {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Ocurrió un error interno. Ya quedó registrado.',
                'details': [],
                'request_id': request_id,
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
