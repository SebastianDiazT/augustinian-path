from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .validators import validate_institutional_email


class User(AbstractUser):
    """Usuario de Ruta UNSA identificado mediante correo electrónico."""

    username = None

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )

    email = models.EmailField(
        _('correo electrónico'),
        unique=True,
        validators=[validate_institutional_email],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    def save(self, *args, **kwargs) -> None:
        self.email = UserManager.normalize_email(self.email).lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
