from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.core.exceptions import ValidationError
from django.http import HttpRequest

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
