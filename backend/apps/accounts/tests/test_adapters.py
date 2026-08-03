from unittest.mock import patch

from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter,
)
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

    @patch.object(
        DefaultSocialAccountAdapter,
        'save_user',
    )
    def test_assigns_student_role_to_new_social_user(
        self,
        mocked_save_user,
    ) -> None:
        user = User.objects.create_user(
            email='nuevo.estudiante@unsa.edu.pe',
            password=None,
        )
        sociallogin = SocialLogin(user=user)

        mocked_save_user.return_value = user

        saved_user = self.adapter.save_user(
            self.request,
            sociallogin,
        )

        self.assertEqual(saved_user, user)
        self.assertTrue(
            user.groups.filter(
                name='student',
            ).exists()
        )
        mocked_save_user.assert_called_once_with(
            self.request,
            sociallogin,
            None,
        )
