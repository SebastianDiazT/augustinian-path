import logging
from typing import Any
from uuid import uuid4

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .constants import API_VERSION

ERROR_TITLES: dict[int, str] = {
    400: 'Solicitud inválida',
    401: 'Autenticación requerida',
    403: 'Acceso denegado',
    404: 'Recurso no encontrado',
    405: 'Método no permitido',
    429: 'Demasiadas solicitudes',
    500: 'Error interno del servidor',
}

logger = logging.getLogger(__name__)


def api_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    response = drf_exception_handler(exc, context)

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
        problem_code = str(getattr(exc, 'default_code', 'api_error')).replace('_', '-')

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


def _extract_error_content(
    data: Any,
) -> tuple[str, Any | None]:
    if isinstance(data, dict) and set(data) == {'detail'}:
        return str(data['detail']), None

    return (
        'La solicitud contiene datos inválidos.',
        data,
    )
