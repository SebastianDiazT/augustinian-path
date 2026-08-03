from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


INSTITUTIONAL_EMAIL_DOMAIN = "unsa.edu.pe"


def validate_institutional_email(value: str) -> None:
    """Valida que el correo pertenezca al dominio institucional de la UNSA."""

    normalized_email = value.strip().lower()
    local_part, separator, domain = normalized_email.rpartition("@")

    if not separator or not local_part or domain != INSTITUTIONAL_EMAIL_DOMAIN:
        raise ValidationError(
            _("Debes utilizar un correo institucional @unsa.edu.pe."),
            code="invalid_institutional_email",
        )
