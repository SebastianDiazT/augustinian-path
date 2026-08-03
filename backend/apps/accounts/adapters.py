from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .validators import validate_institutional_email


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

        return super().is_open_for_signup(
            request,
            sociallogin,
        )
