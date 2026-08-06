from dataclasses import dataclass
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

INSTITUTIONAL_DOMAIN = 'unsa.edu.pe'
MAX_AVATAR_URL_LENGTH = 2048


class InvalidGoogleCredential(ValueError):
    """La credencial de Google no es válida para Ruta Agustina."""


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    subject: str
    email: str
    first_name: str
    last_name: str
    avatar_url: str


def verify_google_credential(credential: str) -> GoogleIdentity:
    credential = credential.strip()

    if not credential:
        raise InvalidGoogleCredential(
            'La credencial de Google es obligatoria.',
        )

    client_id = settings.GOOGLE_OAUTH_CLIENT_ID.strip()

    if not client_id:
        raise ImproperlyConfigured(
            'GOOGLE_OAUTH_CLIENT_ID no está configurado.',
        )

    try:
        payload = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as error:
        raise InvalidGoogleCredential(
            'La credencial de Google no es válida.',
        ) from error

    subject = _required_text_claim(payload, 'sub')
    email = _required_text_claim(payload, 'email').lower()
    hosted_domain = _required_text_claim(payload, 'hd').lower()

    if payload.get('email_verified') is not True:
        raise InvalidGoogleCredential(
            'Google no verificó el correo electrónico.',
        )

    if hosted_domain != INSTITUTIONAL_DOMAIN:
        raise InvalidGoogleCredential(
            'La cuenta no pertenece al dominio institucional.',
        )

    email_parts = email.rsplit('@', maxsplit=1)

    if (
        len(email_parts) != 2
        or not email_parts[0]
        or email_parts[1] != INSTITUTIONAL_DOMAIN
    ):
        raise InvalidGoogleCredential(
            'El correo no pertenece al dominio institucional.',
        )

    return GoogleIdentity(
        subject=subject,
        email=email,
        first_name=_optional_text_claim(
            payload,
            'given_name',
        ),
        last_name=_optional_text_claim(
            payload,
            'family_name',
        ),
        avatar_url=_safe_avatar_url(
            payload.get('picture'),
        ),
    )


def _required_text_claim(
    payload: dict,
    claim_name: str,
) -> str:
    value = payload.get(claim_name)

    if not isinstance(value, str):
        raise InvalidGoogleCredential(
            f'La credencial no contiene el claim {claim_name}.',
        )

    value = value.strip()

    if not value:
        raise InvalidGoogleCredential(
            f'La credencial no contiene el claim {claim_name}.',
        )

    return value


def _optional_text_claim(
    payload: dict,
    claim_name: str,
) -> str:
    value = payload.get(claim_name)

    if not isinstance(value, str):
        return ''

    return value.strip()


def _safe_avatar_url(value: object) -> str:
    if not isinstance(value, str):
        return ''

    value = value.strip()

    if not value or len(value) > MAX_AVATAR_URL_LENGTH:
        return ''

    try:
        parsed_value = urlsplit(value)
    except ValueError:
        return ''

    if parsed_value.scheme != 'https' or not parsed_value.netloc:
        return ''

    return value
