from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary='Estado de salud del servicio',
        description=(
            'Verifica que el servicio esté arriba y que exista conectividad '
            'real a la base de datos.'
        ),
        responses={
            200: OpenApiResponse(
                description='El servicio y la base de datos funcionan correctamente.'
            ),
            503: OpenApiResponse(
                description='El servicio está degradado (ej. la base de datos no responde).'
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        database_ok = self._check_database()

        payload = {
            'status': 'ok' if database_ok else 'degraded',
            'database': 'ok' if database_ok else 'error',
        }
        http_status = status.HTTP_200_OK if database_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(payload, status=http_status)

    @staticmethod
    def _check_database() -> bool:
        try:
            connection.ensure_connection()
            return True
        except Exception:
            return False
