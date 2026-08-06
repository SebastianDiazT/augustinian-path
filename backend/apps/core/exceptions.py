import logging
from typing import Any
from uuid import uuid4

from django.core.exceptions import (
    NON_FIELD_ERRORS,
    BadRequest,
    ObjectDoesNotExist,
    SuspiciousOperation,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DataError, IntegrityError
from django.db.models.deletion import ProtectedError, RestrictedError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound, ParseError
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler as drf_exception_handler

from .constants import API_VERSION

ERROR_TITLES: dict[int, str] = {
    400: 'Solicitud inválida',
    401: 'Autenticación requerida',
    403: 'Acceso denegado',
    404: 'Recurso no encontrado',
    405: 'Método no permitido',
    409: 'Conflicto',
    429: 'Demasiadas solicitudes',
    500: 'Error interno del servidor',
}

logger = logging.getLogger(__name__)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = (
        'La operación entra en conflicto con el estado actual de los datos.'
    )
    default_code = 'conflict'


def api_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    handled_exception = _normalize_exception(exc)
    response = drf_exception_handler(
        handled_exception,
        context,
    )

    request = context.get('request')
    request_id = getattr(request, 'request_id', None) or str(uuid4())

    if response is None:
        logger.error(
            'Unhandled API exception.',
            exc_info=(
                type(exc),
                exc,
                exc.__traceback__,
            ),
            extra={
                'request_id': str(request_id),
            },
        )

        response = Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        detail = 'Ha ocurrido un error interno del servidor.'
        errors = None
        problem_code = 'internal-server-error'
    else:
        detail, errors = _extract_error_content(
            response.data,
        )
        problem_code = str(
            getattr(
                handled_exception,
                'default_code',
                'api_error',
            )
        ).replace('_', '-')

    error: dict[str, Any] = {
        'type': f'urn:augustinian-path:problem:{problem_code}',
        'title': ERROR_TITLES.get(
            response.status_code,
            'Error de la API',
        ),
        'status': response.status_code,
        'detail': detail,
        'instance': getattr(request, 'path', None),
    }

    if errors is not None:
        error['errors'] = errors

    response.data = {
        'error': error,
        'meta': {
            'request_id': request_id,
            'api_version': API_VERSION,
            'timestamp': timezone.now().isoformat(),
        },
    }

    return response


def _normalize_exception(exc: Exception) -> Exception:
    if isinstance(exc, DjangoValidationError):
        return serializers.ValidationError(
            _django_validation_error_detail(exc),
        )

    if isinstance(exc, (ProtectedError, RestrictedError)):
        return Conflict(
            detail=(
                'No se puede completar la operación porque existen '
                'recursos relacionados que deben conservarse.'
            ),
        )

    if isinstance(exc, IntegrityError):
        return Conflict()

    if isinstance(exc, DataError):
        return serializers.ValidationError(
            {
                api_settings.NON_FIELD_ERRORS_KEY: [
                    'Uno o más datos no tienen un formato o tamaño válido.',
                ],
            }
        )

    if isinstance(exc, ObjectDoesNotExist):
        return NotFound()

    if isinstance(exc, (BadRequest, SuspiciousOperation)):
        return ParseError(
            detail='La solicitud no pudo ser procesada.',
        )

    return exc


def _django_validation_error_detail(
    exc: DjangoValidationError,
) -> dict[str, list[str]] | list[str]:
    if hasattr(exc, 'error_dict'):
        return {
            (
                api_settings.NON_FIELD_ERRORS_KEY
                if field == NON_FIELD_ERRORS
                else field
            ): [str(message) for message in messages]
            for field, messages in exc.message_dict.items()
        }

    return [str(message) for message in exc.messages]


def _extract_error_content(
    data: Any,
) -> tuple[str, Any | None]:
    if isinstance(data, dict) and set(data) == {'detail'}:
        return str(data['detail']), None

    return (
        'La solicitud contiene datos inválidos.',
        data,
    )
