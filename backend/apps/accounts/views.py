from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.responses import success_response

from .serializers import (
    CSRFDataSerializer,
    CurrentUserSerializer,
    LogoutDataSerializer,
)


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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Establecer la cookie CSRF',
        tags=['Autenticación'],
        responses=CSRFDataSerializer,
    )
    def get(self, request: Request) -> Response:
        return success_response(
            data={
                'csrf_cookie_set': True,
            },
            request_id=request.request_id,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Cerrar la sesión actual',
        tags=['Autenticación'],
        request=None,
        responses=LogoutDataSerializer,
    )
    def post(self, request: Request) -> Response:
        logout(request)

        return success_response(
            data={
                'authenticated': False,
            },
            request_id=request.request_id,
        )
