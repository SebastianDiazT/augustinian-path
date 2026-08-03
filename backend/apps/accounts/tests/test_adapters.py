from unittest.mock import patch

from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter,
)
from allauth.socialaccount.models import SocialLogin
from django.test import RequestFactory, TestCase

from apps.accounts.adapters import (
    InstitutionalSocialAccountAdapter,
)
from apps.accounts.models import User


class InstitutionalSocialAccountAdapterTests(TestCase):
    def setUp(self) -> None:
        self.adapter = InstitutionalSocialAccountAdapter()
        self.request = RequestFactory().get('/')

    def test_rejects_non_institutional_email(self) -> None:
        sociallogin = SocialLogin(
            user=User(email='persona@gmail.com'),
        )

        is_open = self.adapter.is_open_for_signup(
            self.request,
            sociallogin,
        )

        self.assertFalse(is_open)

    @patch.object(
        DefaultSocialAccountAdapter,
        'is_open_for_signup',
        return_value=True,
    )
    def test_accepts_institutional_email(
        self,
        mocked_is_open_for_signup,
    ) -> None:
        sociallogin = SocialLogin(
            user=User(email='ESTUDIANTE@UNSA.EDU.PE'),
        )

        is_open = self.adapter.is_open_for_signup(
            self.request,
            sociallogin,
        )

        self.assertTrue(is_open)
        mocked_is_open_for_signup.assert_called_once_with(
            self.request,
            sociallogin,
        )

    def test_rejects_missing_email(self) -> None:
        sociallogin = SocialLogin(
            user=User(email=''),
        )

        is_open = self.adapter.is_open_for_signup(
            self.request,
            sociallogin,
        )

        self.assertFalse(is_open)
