from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer

ALLOWED_EMAIL_DOMAIN = '@unsa.edu.pe'


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.data.get('id_token') or request.data.get('credential')
        if not token:
            raise AuthenticationFailed('Falta el token de Google (id_token o credential).')

        try:
            payload = google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError as exc:
            raise AuthenticationFailed(f'Token de Google inválido: {exc}') from exc

        email = payload.get('email', '')

        if not payload.get('email_verified'):
            raise AuthenticationFailed('El correo de Google no está verificado.')

        if not email.lower().endswith(ALLOWED_EMAIL_DOMAIN):
            raise AuthenticationFailed(f'Solo se permiten cuentas {ALLOWED_EMAIL_DOMAIN}.')

        google_sub = payload['sub']
        full_name = payload.get('name', email)
        picture_url = payload.get('picture', '')

        try:
            user = User.objects.get(email=email.lower())

            if user.google_sub and user.google_sub != google_sub:
                raise AuthenticationFailed(
                    'El identificador de Google no coincide con el registrado en el sistema.'
                )

            if not user.google_sub:
                user.google_sub = google_sub
                user.save(update_fields=['google_sub'])

        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email.lower(),
                full_name=full_name,
                google_sub=google_sub,
                picture_url=picture_url,
            )

        if not user.is_active:
            raise AuthenticationFailed('Esta cuenta está desactivada.')

        changed_fields = []
        if user.full_name != full_name:
            user.full_name = full_name
            changed_fields.append('full_name')
        if user.picture_url != picture_url:
            user.picture_url = picture_url
            changed_fields.append('picture_url')

        if changed_fields:
            user.save(update_fields=changed_fields)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data,
            }
        )
