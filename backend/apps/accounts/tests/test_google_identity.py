from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.accounts.google_identity import (
    GoogleIdentity,
    InvalidGoogleCredential,
    verify_google_credential,
)


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID='google-client-id',
)
class VerifyGoogleCredentialTests(SimpleTestCase):
    @patch(
        'apps.accounts.google_identity.id_token.verify_oauth2_token',
    )
    def test_returns_verified_institutional_identity(
        self,
        verify_token,
    ) -> None:
        verify_token.return_value = {
            'sub': 'google-subject-123',
            'email': 'Estudiante@UNSA.EDU.PE',
            'email_verified': True,
            'hd': 'unsa.edu.pe',
            'given_name': ' Sebastian ',
            'family_name': ' Diaz ',
            'picture': ('https://lh3.googleusercontent.com/a/example-avatar'),
        }

        identity = verify_google_credential(
            'google-id-token',
        )

        self.assertEqual(
            identity,
            GoogleIdentity(
                subject='google-subject-123',
                email='estudiante@unsa.edu.pe',
                first_name='Sebastian',
                last_name='Diaz',
                avatar_url=('https://lh3.googleusercontent.com/a/example-avatar'),
            ),
        )

        verify_token.assert_called_once()
        self.assertEqual(
            verify_token.call_args.args[0],
            'google-id-token',
        )
        self.assertEqual(
            verify_token.call_args.args[2],
            'google-client-id',
        )

    @patch(
        'apps.accounts.google_identity.id_token.verify_oauth2_token',
    )
    def test_rejects_invalid_google_token(
        self,
        verify_token,
    ) -> None:
        verify_token.side_effect = ValueError(
            'Invalid token',
        )

        with self.assertRaises(
            InvalidGoogleCredential,
        ):
            verify_google_credential(
                'invalid-token',
            )

    @patch(
        'apps.accounts.google_identity.id_token.verify_oauth2_token',
    )
    def test_rejects_unverified_email(
        self,
        verify_token,
    ) -> None:
        verify_token.return_value = {
            'sub': 'google-subject-123',
            'email': 'estudiante@unsa.edu.pe',
            'email_verified': False,
            'hd': 'unsa.edu.pe',
        }

        with self.assertRaises(
            InvalidGoogleCredential,
        ):
            verify_google_credential(
                'google-id-token',
            )

    @patch(
        'apps.accounts.google_identity.id_token.verify_oauth2_token',
    )
    def test_rejects_non_institutional_account(
        self,
        verify_token,
    ) -> None:
        verify_token.return_value = {
            'sub': 'google-subject-123',
            'email': 'estudiante@gmail.com',
            'email_verified': True,
            'hd': 'gmail.com',
        }

        with self.assertRaises(
            InvalidGoogleCredential,
        ):
            verify_google_credential(
                'google-id-token',
            )

    @patch(
        'apps.accounts.google_identity.id_token.verify_oauth2_token',
    )
    def test_ignores_insecure_avatar_url(
        self,
        verify_token,
    ) -> None:
        verify_token.return_value = {
            'sub': 'google-subject-123',
            'email': 'estudiante@unsa.edu.pe',
            'email_verified': True,
            'hd': 'unsa.edu.pe',
            'picture': 'http://example.com/avatar.png',
        }

        identity = verify_google_credential(
            'google-id-token',
        )

        self.assertEqual(
            identity.avatar_url,
            '',
        )
