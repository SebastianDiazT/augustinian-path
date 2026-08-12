from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import CatalogBaseModel


class CourseEnrollment(CatalogBaseModel):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'En curso'
        PASSED = 'passed', 'Aprobado'
        FAILED = 'failed', 'Desaprobado'
        WITHDRAWN = 'withdrawn', 'Retirado'

    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='course_enrollments',
    )
    offering = models.ForeignKey(
        'offerings.Offering', on_delete=models.PROTECT, related_name='enrollments',
    )
    theory_section = models.ForeignKey(
        'offerings.Section', on_delete=models.PROTECT, related_name='theory_enrollments',
    )
    lab_section = models.ForeignKey(
        'offerings.Section', on_delete=models.PROTECT, null=True, blank=True,
        related_name='lab_enrollments',
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)

    class Meta:
        db_table = 'academic_records_course_enrollment'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'offering'], name='unique_enrollment_per_offering',
            ),
        ]

    def __str__(self):
        return f'{self.student} — {self.offering}'

    def get_school(self):
        return self.offering.get_school()

    def get_syllabus(self):
        from apps.curricula.models import Syllabus

        return Syllabus.objects.filter(
            course=self.offering.course, academic_term=self.offering.academic_term,
        ).first()

    def compute_weighted_average(self):
        total = Decimal('0')
        for grade in self.grades.select_related('evaluation_component'):
            total += grade.score * grade.evaluation_component.weight / Decimal('100')
        return total


class Grade(CatalogBaseModel):
    enrollment = models.ForeignKey(
        CourseEnrollment, on_delete=models.CASCADE, related_name='grades',
    )
    evaluation_component = models.ForeignKey(
        'curricula.EvaluationComponent', on_delete=models.PROTECT, related_name='grades',
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('20'))],
    )

    class Meta:
        db_table = 'academic_records_grade'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'evaluation_component'],
                name='unique_grade_per_component',
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=0) & models.Q(score__lte=20),
                name='score_between_0_and_20',
            ),
        ]

    def __str__(self):
        return f'{self.enrollment} — {self.evaluation_component.name}: {self.score}'
