from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)

from apps.accounts.jwt_tokens import issue_token_pair
from apps.accounts.models import User


class RefreshTokenEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/refresh/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            google_subject='google-subject-123',
        )

    def test_rotates_refresh_token(self) -> None:
        token_pair = issue_token_pair(self.user)
        old_refresh_token = RefreshToken(
            token_pair.refresh,
        )
        old_jti = old_refresh_token['jti']

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

        data = response.json()['data']

        self.assertIn(
            'access',
            data,
        )
        self.assertIn(
            'refresh',
            data,
        )
        self.assertNotEqual(
            data['refresh'],
            token_pair.refresh,
        )

        new_access_token = AccessToken(
            data['access'],
        )
        new_refresh_token = RefreshToken(
            data['refresh'],
        )

        self.assertEqual(
            new_access_token['sub'],
            str(self.user.public_id),
        )
        self.assertEqual(
            new_refresh_token['sub'],
            str(self.user.public_id),
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=old_jti,
            ).exists()
        )

    def test_rejects_reused_refresh_token(
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
        self.assertIn(
            'error',
            second_response.json(),
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
        self.assertIn(
            'error',
            response.json(),
        )

    def test_rejects_refresh_for_inactive_user(
        self,
    ) -> None:
        token_pair = issue_token_pair(self.user)

        self.user.is_active = False
        self.user.save(
            update_fields=[
                'is_active',
            ],
        )

        response = self.client.post(
            self.endpoint,
            {
                'refresh': token_pair.refresh,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
