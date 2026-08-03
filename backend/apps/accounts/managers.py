from typing import Any

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager para usuarios identificados mediante correo electrónico."""

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        normalized_email = self.normalize_email(email).lower()

        user = self.model(
            email=normalized_email,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
