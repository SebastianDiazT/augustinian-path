from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.core.models import CatalogBaseModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, CatalogBaseModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)
    picture_url = models.URLField(blank=True)
    cui = models.CharField(max_length=20, unique=True, null=True, blank=True)

    is_platform_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.cui if self.cui else "Sin CUI"}'