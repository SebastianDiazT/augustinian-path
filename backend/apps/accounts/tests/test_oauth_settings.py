from django.conf import settings
from django.test import SimpleTestCase


class GoogleOAuthSettingsTests(SimpleTestCase):
    def test_login_requests_only_identity_scopes(self) -> None:
        google_settings = settings.SOCIALACCOUNT_PROVIDERS['google']

        self.assertEqual(
            google_settings['SCOPE'],
            [
                'profile',
                'email',
            ],
        )
        self.assertNotIn(
            'AUTH_PARAMS',
            google_settings,
        )
        self.assertTrue(
            google_settings['OAUTH_PKCE_ENABLED'],
        )
