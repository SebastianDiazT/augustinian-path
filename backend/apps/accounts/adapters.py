from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .roles import Role
from .validators import validate_institutional_email


class GoogleOnlyAccountAdapter(DefaultAccountAdapter):
    """Deshabilita el registro tradicional de cuentas."""

    def is_open_for_signup(
        self,
        request: HttpRequest,
    ) -> bool:
        return False


class InstitutionalSocialAccountAdapter(
    DefaultSocialAccountAdapter,
):
    """Restringe el registro social a cuentas institucionales UNSA."""

    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        email = sociallogin.user.email or ''

        try:
            validate_institutional_email(email)
        except ValidationError:
            return False

        return True

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        form=None,
    ):
        user = super().save_user(
            request,
            sociallogin,
            form,
        )

        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )
        user.groups.add(student_group)

        return user
