from uuid import uuid4

from django.db import models

from .catalog import Course
from .curriculum import CurriculumCourse


class AcademicPeriod(models.Model):
    """Periodo académico en el que se dictan asignaturas."""

    class Term(models.TextChoices):
        FIRST = 'A', 'Primer semestre'
        SECOND = 'B', 'Segundo semestre'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    year = models.PositiveSmallIntegerField()
    term = models.CharField(
        max_length=1,
        choices=Term.choices,
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
            '-year',
            'term',
        ]
        verbose_name = 'periodo académico'
        verbose_name_plural = 'periodos académicos'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'year',
                    'term',
                ],
                name='unique_academic_period_year_term',
            ),
        ]

    @property
    def code(self) -> str:
        return f'{self.year}-{self.term}'

    def __str__(self) -> str:
        return self.code


class CourseOffering(models.Model):
    """Oferta de una asignatura disponible en un periodo académico."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name='course_offerings',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='offerings',
    )
    curriculum_courses = models.ManyToManyField(
        CurriculumCourse,
        related_name='course_offerings',
        blank=True,
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
            '-academic_period__year',
            'academic_period__term',
            'course__code',
        ]
        verbose_name = 'oferta de asignatura'
        verbose_name_plural = 'ofertas de asignaturas'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'academic_period',
                    'course',
                ],
                name='unique_course_per_academic_period',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.academic_period.code}: {self.course.code}'
