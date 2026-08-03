from uuid import uuid4

from django.db import models
from django.db.models.functions import Lower


class Faculty(models.Model):
    """Facultad perteneciente a la Universidad Nacional de San Agustín."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        max_length=150,
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
        ordering = ['name']
        verbose_name = 'facultad'
        verbose_name_plural = 'facultades'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_faculty_name_case_insensitive',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='faculty_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProfessionalSchool(models.Model):
    """Escuela profesional perteneciente a una facultad de la UNSA."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name='professional_schools',
    )
    name = models.CharField(
        max_length=150,
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
            'faculty__name',
            'name',
        ]
        verbose_name = 'escuela profesional'
        verbose_name_plural = 'escuelas profesionales'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'faculty',
                name='unique_school_name_per_faculty_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='professional_school_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} ({self.faculty.name})'


class CurriculumPlan(models.Model):
    """Versión de un plan de estudios de una escuela profesional."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    professional_school = models.ForeignKey(
        ProfessionalSchool,
        on_delete=models.PROTECT,
        related_name='curriculum_plans',
    )
    code = models.CharField(
        max_length=30,
    )
    name = models.CharField(
        max_length=150,
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
        verbose_name = 'plan de estudios'
        verbose_name_plural = 'planes de estudios'
        constraints = [
            models.UniqueConstraint(
                Lower('code'),
                'professional_school',
                name='unique_plan_code_per_school_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(code=''),
                name='curriculum_plan_code_not_empty',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='curriculum_plan_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.code = ' '.join(self.code.split()).upper()
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.code} — {self.name} ({self.professional_school.name})'
