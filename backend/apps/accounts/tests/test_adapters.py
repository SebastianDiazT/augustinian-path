from unittest.mock import patch

from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter,
)
from allauth.socialaccount.models import (
    SocialAccount,
    SocialLogin,
)
from django.test import RequestFactory, TestCase

from apps.accounts.adapters import (
    GoogleOnlyAccountAdapter,
    InstitutionalSocialAccountAdapter,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class GoogleOnlyAccountAdapterTests(TestCase):
    def test_disables_regular_signup(self) -> None:
        request = RequestFactory().get('/')
        adapter = GoogleOnlyAccountAdapter()

        self.assertFalse(adapter.is_open_for_signup(request))


class InstitutionalSocialAccountAdapterTests(TestCase):
    def setUp(self) -> None:
        self.adapter = InstitutionalSocialAccountAdapter()
        self.request = RequestFactory().get('/')

    def create_google_social_login(
        self,
        user: User,
        *,
        given_name: str | None = None,
        family_name: str | None = None,
    ) -> SocialLogin:
        extra_data = {}

        if given_name is not None:
            extra_data['given_name'] = given_name

        if family_name is not None:
            extra_data['family_name'] = family_name

        return SocialLogin(
            user=user,
            account=SocialAccount(
                user=user,
                provider='google',
                uid='google-user-123',
                extra_data=extra_data,
            ),
        )

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

    @patch.object(
        DefaultSocialAccountAdapter,
        'pre_social_login',
    )
    def test_synchronizes_names_for_existing_google_user(
        self,
        mocked_pre_social_login,
    ) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            first_name='',
            last_name='',
        )
        sociallogin = self.create_google_social_login(
            user,
            given_name='  SEBASTIAN  ',
            family_name='  DIAZ TICONA  ',
        )

        self.adapter.pre_social_login(
            self.request,
            sociallogin,
        )

        user.refresh_from_db()

        self.assertEqual(
            user.first_name,
            'SEBASTIAN',
        )
        self.assertEqual(
            user.last_name,
            'DIAZ TICONA',
        )
        mocked_pre_social_login.assert_called_once_with(
            self.request,
            sociallogin,
        )

    @patch.object(
        DefaultSocialAccountAdapter,
        'save_user',
    )
    def test_synchronizes_names_for_new_google_user(
        self,
        mocked_save_user,
    ) -> None:
        user = User.objects.create_user(
            email='nuevo.estudiante@unsa.edu.pe',
            password=None,
            first_name='',
            last_name='',
        )
        sociallogin = self.create_google_social_login(
            user,
            given_name='SEBASTIAN',
            family_name='DIAZ TICONA',
        )

        mocked_save_user.return_value = user

        saved_user = self.adapter.save_user(
            self.request,
            sociallogin,
        )

        saved_user.refresh_from_db()

        self.assertEqual(
            saved_user.first_name,
            'SEBASTIAN',
        )
        self.assertEqual(
            saved_user.last_name,
            'DIAZ TICONA',
        )
        self.assertTrue(
            saved_user.groups.filter(
                name=Role.STUDENT.value,
            ).exists()
        )

    @patch.object(
        DefaultSocialAccountAdapter,
        'pre_social_login',
    )
    def test_preserves_name_when_google_omits_value(
        self,
        mocked_pre_social_login,
    ) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password=None,
            first_name='Nombre local',
            last_name='Apellido local',
        )
        sociallogin = self.create_google_social_login(
            user,
            given_name='Nuevo nombre',
            family_name='   ',
        )

        self.adapter.pre_social_login(
            self.request,
            sociallogin,
        )

        user.refresh_from_db()

        self.assertEqual(
            user.first_name,
            'Nuevo nombre',
        )
        self.assertEqual(
            user.last_name,
            'Apellido local',
        )
        mocked_pre_social_login.assert_called_once_with(
            self.request,
            sociallogin,
        )
