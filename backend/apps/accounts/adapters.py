from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter,
)
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .models import User
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
    """Restringe y sincroniza las cuentas institucionales UNSA."""

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

    def pre_social_login(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> None:
        super().pre_social_login(
            request,
            sociallogin,
        )

        if sociallogin.user.pk is None:
            return

        self._synchronize_google_names(
            sociallogin.user,
            sociallogin,
        )

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        form=None,
    ) -> User:
        user = super().save_user(
            request,
            sociallogin,
            form,
        )

        self._synchronize_google_names(
            user,
            sociallogin,
        )

        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )
        user.groups.add(student_group)

        return user

    @staticmethod
    def _synchronize_google_names(
        user: User,
        sociallogin: SocialLogin,
    ) -> None:
        account = getattr(
            sociallogin,
            'account',
            None,
        )

        if account is None or account.provider != 'google':
            return

        extra_data = account.extra_data

        if not isinstance(extra_data, dict):
            return

        provider_names = {
            'first_name': extra_data.get('given_name'),
            'last_name': extra_data.get('family_name'),
        }
        updated_fields: list[str] = []

        for field_name, provider_value in provider_names.items():
            if not isinstance(provider_value, str):
                continue

            provider_value = provider_value.strip()

            if not provider_value or getattr(user, field_name) == provider_value:
                continue

            setattr(
                user,
                field_name,
                provider_value,
            )
            updated_fields.append(field_name)

        if user.pk is not None and updated_fields:
            user.save(
                update_fields=updated_fields,
            )
