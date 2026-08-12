from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for Ruta Agustina's custom user model.

    There is no 'username': the user's identity is their institutional
    email (@unsa.edu.pe). Normal app login happens via Google (see
    accounts.auth_views.GoogleLoginView), so most users won't have a
    usable password; passwords are only used for Django admin
    superuser accounts.
    """

    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_platform_admin', False)
        extra_fields.setdefault('full_name', extra_fields.get('full_name', email))
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_platform_admin', True)
        extra_fields.setdefault('full_name', extra_fields.get('full_name', email))

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
