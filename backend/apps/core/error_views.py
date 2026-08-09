import logging

from django.http import JsonResponse

from .error_payload import build_error_payload

logger = logging.getLogger(__name__)


def custom_404_view(request, exception=None):
    return JsonResponse(
        build_error_payload('NOT_FOUND', 'El recurso solicitado no existe.'),
        status=404,
    )


def custom_500_view(request):
    logger.exception('Error interno no controlado fuera del ciclo de DRF')
    return JsonResponse(
        build_error_payload(
            'INTERNAL_ERROR',
            'Ocurrió un error interno. Intenta nuevamente más tarde.',
        ),
        status=500,
    )
