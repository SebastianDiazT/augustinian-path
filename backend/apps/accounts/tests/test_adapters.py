from allauth.socialaccount.models import SocialLogin
from django.test import RequestFactory, TestCase

from apps.accounts.adapters import (
    GoogleOnlyAccountAdapter,
    InstitutionalSocialAccountAdapter,
)
from apps.accounts.models import User


class GoogleOnlyAccountAdapterTests(TestCase):
    def test_disables_regular_signup(self) -> None:
        request = RequestFactory().get('/')
        adapter = GoogleOnlyAccountAdapter()

        self.assertFalse(adapter.is_open_for_signup(request))


class InstitutionalSocialAccountAdapterTests(TestCase):
    def setUp(self) -> None:
        self.adapter = InstitutionalSocialAccountAdapter()
        self.request = RequestFactory().get('/')

    def test_rejects_non_institutional_email(self) -> None:
        sociallogin = SocialLogin(
            user=User(email='persona@gmail.com'),
        )

        self.assertFalse(
            self.adapter.is_open_for_signup(
                self.request,
                sociallogin,
            )
        )

    def test_accepts_institutional_email(self) -> None:
        sociallogin = SocialLogin(
            user=User(email='ESTUDIANTE@UNSA.EDU.PE'),
        )

        self.assertTrue(
            self.adapter.is_open_for_signup(
                self.request,
                sociallogin,
            )
        )

    def test_rejects_missing_email(self) -> None:
        sociallogin = SocialLogin(
            user=User(email=''),
        )

        self.assertFalse(
            self.adapter.is_open_for_signup(
                self.request,
                sociallogin,
            )
        )
