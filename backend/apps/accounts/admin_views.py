from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.responses import success_response

from .permissions import IsPlatformAdmin
from .serializers import PlatformAdminAccessDataSerializer


class PlatformAdminAccessView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Comprobar acceso administrativo',
        tags=['Administración'],
        responses=PlatformAdminAccessDataSerializer,
    )
    def get(self, request: Request) -> Response:
        return success_response(
            data={
                'authorized': True,
            },
            request_id=request.request_id,
        )
