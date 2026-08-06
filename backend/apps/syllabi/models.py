from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.academics.models import CourseOffering, CurriculumCourse


class Syllabus(models.Model):
    """Contenido oficial del sílabo para una oferta y versión de malla."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Borrador'
        PUBLISHED = 'PUBLISHED', 'Publicado'
        ARCHIVED = 'ARCHIVED', 'Archivado'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='syllabi',
    )
    curriculum_course = models.ForeignKey(
        CurriculumCourse,
        on_delete=models.PROTECT,
        related_name='syllabi',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    duration_weeks = models.PositiveSmallIntegerField(
        default=17,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(52),
        ],
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
    )
    foundation = models.TextField(
        blank=True,
        default='',
    )
    instructors = models.JSONField(
        default=list,
        blank=True,
    )
    competencies = models.JSONField(
        default=list,
        blank=True,
    )
    thematic_content = models.JSONField(
        default=list,
        blank=True,
    )
    teaching_methods = models.TextField(
        blank=True,
        default='',
    )
    teaching_media = models.TextField(
        blank=True,
        default='',
    )
    organization_forms = models.TextField(
        blank=True,
        default='',
    )
    formative_research = models.TextField(
        blank=True,
        default='',
    )
    social_responsibility = models.TextField(
        blank=True,
        default='',
    )
    weekly_schedule = models.JSONField(
        default=list,
        blank=True,
    )
    evaluation_strategy = models.TextField(
        blank=True,
        default='',
    )
    evaluation_schedule = models.JSONField(
        default=list,
        blank=True,
    )
    approval_requirements = models.TextField(
        blank=True,
        default='',
    )
    bibliography = models.JSONField(
        default=list,
        blank=True,
    )
    source_document_url = models.URLField(
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            '-course_offering__academic_period__year',
            'course_offering__academic_period__term',
            'course_offering__course__code',
        ]
        verbose_name = 'sílabo'
        verbose_name_plural = 'sílabos'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'course_offering',
                    'curriculum_course',
                ],
                name='unique_syllabus_per_offering_curriculum',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        errors = {}

        if (
            self.course_offering_id is not None
            and self.curriculum_course_id is not None
            and not self.course_offering.curriculum_courses.filter(
                pk=self.curriculum_course_id,
            ).exists()
        ):
            errors['curriculum_course'] = (
                'La entrada de malla no está vinculada a la oferta.'
            )

        json_fields = (
            'instructors',
            'competencies',
            'thematic_content',
            'weekly_schedule',
            'evaluation_schedule',
            'bibliography',
        )

        for field_name in json_fields:
            if not isinstance(getattr(self, field_name), list):
                errors[field_name] = 'Este campo debe ser una lista.'

        if self.status == self.Status.PUBLISHED:
            required_text_fields = (
                'foundation',
                'teaching_methods',
                'teaching_media',
                'organization_forms',
                'evaluation_strategy',
                'approval_requirements',
            )

            for field_name in required_text_fields:
                if not str(getattr(self, field_name)).strip():
                    errors[field_name] = (
                        'Este campo es obligatorio para publicar el sílabo.'
                    )

            for field_name in json_fields:
                if not getattr(self, field_name):
                    errors[field_name] = (
                        'Este campo es obligatorio para publicar el sílabo.'
                    )

            if self.publication_date is None:
                errors['publication_date'] = (
                    'La fecha de publicación es obligatoria para publicar.'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f'{self.course_offering.course.code} - '
            f'{self.course_offering.academic_period.code}'
        )
