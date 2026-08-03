from typing import Any

from django.utils import timezone
from rest_framework.response import Response


def success_response(
    *,
    data: Any,
    request_id: str,
    status_code: int = 200,
) -> Response:
    return Response(
        {
            'data': data,
            'meta': {
                'request_id': request_id,
                'api_version': 'v1',
                'timestamp': timezone.now().isoformat(),
            },
        },
        status=status_code,
    )
