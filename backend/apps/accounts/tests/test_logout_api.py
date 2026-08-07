from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.jwt_tokens import issue_token_pair
from apps.accounts.models import User


class LogoutEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/logout/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
        )

    def test_blacklists_refresh_token_without_access_token(
        self,
    ) -> None:
        token_pair = issue_token_pair(self.user)
        refresh_token = RefreshToken(
            token_pair.refresh,
        )
        refresh_jti = refresh_token['jti']

        response = self.client.post(
            self.endpoint,
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data'],
            {
                'revoked': True,
            },
        )
        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=refresh_jti,
            ).exists()
        )

    def test_revoked_token_cannot_be_refreshed(
        self,
    ) -> None:
        token_pair = issue_token_pair(self.user)

        logout_response = self.client.post(
            self.endpoint,
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_response = self.client.post(
            '/api/v1/auth/refresh/',
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_rejects_missing_refresh_token(
        self,
    ) -> None:
        response = self.client.post(
            self.endpoint,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'refresh',
            response.json()['error']['errors'],
        )

    def test_rejects_invalid_refresh_token(
        self,
    ) -> None:
        response = self.client.post(
            self.endpoint,
            {
                'refresh': 'invalid-token',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            response.headers.get('WWW-Authenticate'),
            'Bearer realm="api"',
        )

    def test_rejects_already_revoked_token(
        self,
    ) -> None:
        token_pair = issue_token_pair(self.user)

        first_response = self.client.post(
            self.endpoint,
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.endpoint,
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
