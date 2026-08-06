from uuid import uuid4

from django.db import models
from django.db.models.functions import Lower

from .institution import ProfessionalSchool


class Course(models.Model):
    """Asignatura definida por una escuela profesional de la UNSA."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    professional_school = models.ForeignKey(
        ProfessionalSchool,
        on_delete=models.PROTECT,
        related_name='courses',
    )
    code = models.CharField(
        max_length=30,
    )
    name = models.CharField(
        max_length=200,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            'professional_school__name',
            'code',
        ]
        verbose_name = 'asignatura'
        verbose_name_plural = 'asignaturas'
        constraints = [
            models.UniqueConstraint(
                Lower('code'),
                'professional_school',
                name='unique_course_code_per_school_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(code=''),
                name='course_code_not_empty',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='course_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.code = ' '.join(self.code.split()).upper()
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.code} — {self.name} ({self.professional_school.name})'
