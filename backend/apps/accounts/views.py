from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.responses import success_response

from .serializers import CurrentUserSerializer


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Obtener el usuario autenticado',
        tags=['Autenticación'],
        responses=CurrentUserSerializer,
    )
    def get(self, request: Request) -> Response:
        serializer = CurrentUserSerializer(request.user)

        return success_response(
            data=serializer.data,
            request_id=request.request_id,
        )
