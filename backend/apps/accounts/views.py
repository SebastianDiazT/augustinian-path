from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import Conflict
from apps.core.openapi import success_response_schema
from apps.core.responses import success_response
from apps.core.serializers import ApiErrorResponseSerializer

from .google_identity import (
    InvalidGoogleCredential,
    verify_google_credential,
)
from .google_user import (
    GoogleIdentityConflict,
    synchronize_google_user,
)
from .jwt_tokens import (
    InactiveUser,
    issue_token_pair,
)
from .serializers import (
    CSRFDataSerializer,
    CurrentUserSerializer,
    GoogleLoginDataSerializer,
    GoogleLoginRequestSerializer,
    LogoutDataSerializer,
)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Obtener el usuario autenticado',
        tags=['Autenticación'],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='CurrentUserSuccessResponse',
                data_serializer=CurrentUserSerializer,
            ),
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        serializer = CurrentUserSerializer(request.user)

        return success_response(
            data=serializer.data,
            request_id=request.request_id,
        )


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Iniciar sesión con Google',
        tags=['Autenticación'],
        request=GoogleLoginRequestSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='GoogleLoginSuccessResponse',
                data_serializer=GoogleLoginDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_409_CONFLICT: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        request_serializer = GoogleLoginRequestSerializer(
            data=request.data,
        )
        request_serializer.is_valid(
            raise_exception=True,
        )

        credential = request_serializer.validated_data['credential']

        try:
            identity = verify_google_credential(
                credential,
            )
        except InvalidGoogleCredential as error:
            raise serializers.ValidationError(
                {
                    'credential': [
                        str(error),
                    ],
                }
            ) from error

        try:
            user, is_new_user = synchronize_google_user(
                identity,
            )
        except GoogleIdentityConflict as error:
            raise Conflict(
                detail=str(error),
            ) from error

        try:
            token_pair = issue_token_pair(user)
        except InactiveUser as error:
            raise PermissionDenied(
                detail=str(error),
            ) from error

        user_serializer = CurrentUserSerializer(user)

        return success_response(
            data={
                'access': token_pair.access,
                'refresh': token_pair.refresh,
                'user': user_serializer.data,
                'is_new_user': is_new_user,
            },
            request_id=request.request_id,
        )


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Establecer la cookie CSRF',
        tags=['Autenticación'],
        responses=success_response_schema(
            component_name='CsrfSuccessResponse',
            data_serializer=CSRFDataSerializer,
        ),
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
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='LogoutSuccessResponse',
                data_serializer=LogoutDataSerializer,
            ),
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        logout(request)

        return success_response(
            data={
                'authenticated': False,
            },
            request_id=request.request_id,
        )
