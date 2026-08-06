from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .validators import validate_institutional_email


class User(AbstractUser):
    """Usuario de Ruta Agustina  identificado mediante correo electrónico."""

    username = None

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )

    google_subject = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    avatar_url = models.URLField(
        max_length=2048,
        blank=True,
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


class AcademicAdminAssignment(models.Model):
    """Escuela profesional administrada por un administrador académico."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='academic_admin_assignment',
    )
    professional_school = models.ForeignKey(
        'academics.ProfessionalSchool',
        on_delete=models.PROTECT,
        related_name='academic_admin_assignments',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['user__email']
        verbose_name = 'asignación de administrador académico'
        verbose_name_plural = 'asignaciones de administradores académicos'

    def __str__(self) -> str:
        return f'{self.user.email} — {self.professional_school.name}'
