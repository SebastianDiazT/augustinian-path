from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .curriculum import CurriculumCourse
from .offerings import CourseOffering


class StudentCourseAttempt(models.Model):
    """Resultado de un estudiante en una oferta y entrada concreta de la malla."""

    class Status(models.TextChoices):
        ENROLLED = 'ENROLLED', 'En curso'
        PASSED = 'PASSED', 'Aprobado'
        FAILED = 'FAILED', 'Desaprobado'
        WITHDRAWN = 'WITHDRAWN', 'Retirado'

    PASSING_GRADE = Decimal('10.50')
    MAXIMUM_GRADE = Decimal('20.00')

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_attempts',
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='student_attempts',
    )
    curriculum_course = models.ForeignKey(
        CurriculumCourse,
        on_delete=models.PROTECT,
        related_name='student_attempts',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ENROLLED,
    )
    final_grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(MAXIMUM_GRADE),
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            'student__email',
            '-course_offering__academic_period__year',
            'course_offering__academic_period__term',
            'course_offering__course__code',
        ]
        verbose_name = 'intento académico del estudiante'
        verbose_name_plural = 'intentos académicos de estudiantes'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'student',
                    'course_offering',
                ],
                name='unique_student_course_attempt_per_offering',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(final_grade__isnull=True)
                    | models.Q(
                        final_grade__gte=Decimal('0.00'),
                        final_grade__lte=Decimal('20.00'),
                    )
                ),
                name='student_course_attempt_grade_range',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status='PASSED',
                        final_grade__gte=Decimal('10.50'),
                    )
                    | models.Q(
                        status='FAILED',
                        final_grade__isnull=False,
                        final_grade__lt=Decimal('10.50'),
                    )
                    | models.Q(
                        status__in=[
                            'ENROLLED',
                            'WITHDRAWN',
                        ],
                        final_grade__isnull=True,
                    )
                ),
                name='student_course_attempt_status_grade_consistent',
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

        if self.status == self.Status.PASSED and (
            self.final_grade is None or self.final_grade < self.PASSING_GRADE
        ):
            errors['final_grade'] = (
                'Un curso aprobado requiere una nota final mínima de 10.50.'
            )
        elif self.status == self.Status.FAILED and (
            self.final_grade is None or self.final_grade >= self.PASSING_GRADE
        ):
            errors['final_grade'] = (
                'Un curso desaprobado requiere una nota final menor que 10.50.'
            )
        elif self.status in {
            self.Status.ENROLLED,
            self.Status.WITHDRAWN,
        } and self.final_grade is not None:
            errors['final_grade'] = (
                'Un curso en curso o retirado no debe tener nota final.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f'{self.student.email}: {self.course_offering.course.code} '
            f'({self.get_status_display()})'
        )
