from dataclasses import dataclass

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class InactiveUser(ValueError):
    """No se pueden emitir tokens para una cuenta inactiva."""


@dataclass(frozen=True, slots=True)
class TokenPair:
    access: str
    refresh: str


def issue_token_pair(user: User) -> TokenPair:
    if not user.is_active:
        raise InactiveUser(
            'La cuenta de usuario está desactivada.',
        )

    refresh_token = RefreshToken.for_user(user)

    return TokenPair(
        access=str(refresh_token.access_token),
        refresh=str(refresh_token),
    )
