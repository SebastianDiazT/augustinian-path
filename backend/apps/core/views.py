from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
        except Exception:
            return Response(
                {'status': 'degraded', 'database': 'unreachable'},
                status=503,
            )
        return Response({'status': 'ok', 'database': 'ok'})
