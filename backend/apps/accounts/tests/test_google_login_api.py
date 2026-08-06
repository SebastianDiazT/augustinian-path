from unittest.mock import patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
)

from apps.accounts.google_identity import (
    GoogleIdentity,
    InvalidGoogleCredential,
)
from apps.accounts.google_user import (
    GoogleIdentityConflict,
)
from apps.accounts.models import User


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID='google-client-id',
)
class GoogleLoginEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/google/'

    @patch(
        'apps.accounts.views.verify_google_credential',
    )
    def test_creates_user_and_returns_token_pair(
        self,
        verify_credential,
    ) -> None:
        verify_credential.return_value = self._identity()

        response = self.client.post(
            self.endpoint,
            {
                'credential': 'google-id-token',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertTrue(
            data['is_new_user'],
        )
        self.assertEqual(
            data['user']['email'],
            'estudiante@unsa.edu.pe',
        )
        self.assertEqual(
            data['user']['roles'],
            [
                'student',
            ],
        )

        user = User.objects.get(
            google_subject='google-subject-123',
        )

        access_token = AccessToken(
            data['access'],
        )
        refresh_token = RefreshToken(
            data['refresh'],
        )

        self.assertEqual(
            access_token['sub'],
            str(user.public_id),
        )
        self.assertEqual(
            refresh_token['sub'],
            str(user.public_id),
        )
        self.assertFalse(
            user.has_usable_password(),
        )

        verify_credential.assert_called_once_with(
            'google-id-token',
        )

    @patch(
        'apps.accounts.views.verify_google_credential',
    )
    def test_returns_existing_user(
        self,
        verify_credential,
    ) -> None:
        identity = self._identity()

        User.objects.create_user(
            email=identity.email,
            password=None,
            google_subject=identity.subject,
        )

        verify_credential.return_value = identity

        response = self.client.post(
            self.endpoint,
            {
                'credential': 'google-id-token',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertFalse(
            response.json()['data']['is_new_user'],
        )
        self.assertEqual(
            User.objects.count(),
            1,
        )

    def test_rejects_missing_credential(self) -> None:
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
            'credential',
            response.json()['error']['errors'],
        )

    @patch(
        'apps.accounts.views.verify_google_credential',
    )
    def test_rejects_invalid_google_credential(
        self,
        verify_credential,
    ) -> None:
        verify_credential.side_effect = InvalidGoogleCredential(
            'La credencial de Google no es válida.',
        )

        response = self.client.post(
            self.endpoint,
            {
                'credential': 'invalid-token',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            User.objects.count(),
            0,
        )
        self.assertIn(
            'credential',
            response.json()['error']['errors'],
        )

    @patch(
        'apps.accounts.views.synchronize_google_user',
    )
    @patch(
        'apps.accounts.views.verify_google_credential',
    )
    def test_returns_conflict_for_linked_identity(
        self,
        verify_credential,
        synchronize_user,
    ) -> None:
        verify_credential.return_value = self._identity()
        synchronize_user.side_effect = GoogleIdentityConflict(
            'La identidad de Google pertenece a otro usuario.',
        )

        response = self.client.post(
            self.endpoint,
            {
                'credential': 'google-id-token',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    @staticmethod
    def _identity() -> GoogleIdentity:
        return GoogleIdentity(
            subject='google-subject-123',
            email='estudiante@unsa.edu.pe',
            first_name='Sebastian',
            last_name='Diaz',
            avatar_url=('https://lh3.googleusercontent.com/a/example-avatar'),
        )
