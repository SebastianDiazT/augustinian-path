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

    def test_uses_only_the_browser_headless_client(self) -> None:
        self.assertTrue(settings.HEADLESS_ONLY)
        self.assertEqual(
            settings.HEADLESS_CLIENTS,
            ('browser',),
        )

    def test_social_login_errors_redirect_to_frontend(self) -> None:
        self.assertEqual(
            settings.HEADLESS_FRONTEND_URLS,
            {
                'socialaccount_login_error': (settings.FRONTEND_URL),
            },
        )
