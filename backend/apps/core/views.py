from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .responses import success_response
from .serializers import HealthResponseSerializer


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Comprobar el estado de la API',
        tags=['Sistema'],
        responses=HealthResponseSerializer,
    )
    def get(self, request: Request) -> Response:
        return success_response(
            data={
                'status': 'ok',
                'service': 'ruta-unsa-backend',
            },
            request_id=request.request_id,
        )
