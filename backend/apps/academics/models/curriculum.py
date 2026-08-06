from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from .catalog import Course
from .institution import ProfessionalSchool


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


class CurriculumCourse(models.Model):
    """Ubicación de una asignatura dentro de un plan de estudios."""

    class Component(models.TextChoices):
        BASIC_TRAINING = 'A', 'Formación básica'
        SPECIALIZED_TRAINING = 'B', 'Formación especializada'
        PROFESSIONAL_AND_OTHER = 'C', 'Formación profesional y otros'
        GENERAL_LEARNING = 'D', 'Estudios generales: capacidades de aprendizaje'
        GENERAL_HUMANISTIC = (
            'E',
            'Estudios generales: formación humanista, identidad y ciudadanía',
        )
        SPECIFIC_STUDIES = 'F', 'Estudios específicos'
        SPECIALTY_STUDIES = 'G', 'Estudios de especialidad'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    curriculum_plan = models.ForeignKey(
        CurriculumPlan,
        on_delete=models.PROTECT,
        related_name='curriculum_courses',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='curriculum_entries',
    )
    prerequisites = models.ManyToManyField(
        'self',
        through='CurriculumCoursePrerequisite',
        through_fields=(
            'curriculum_course',
            'prerequisite',
        ),
        symmetrical=False,
        related_name='required_by',
        blank=True,
    )
    cycle = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
    )
    component = models.CharField(
        max_length=1,
        choices=Component.choices,
        default=Component.SPECIFIC_STUDIES,
    )
    credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    prerequisite_credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    theory_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    seminar_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    theory_practice_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    practice_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
        ],
    )
    laboratory_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        validators=[
            MinValueValidator(Decimal('0')),
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
            'curriculum_plan_id',
            'cycle',
            'course__code',
        ]
        verbose_name = 'asignatura del plan'
        verbose_name_plural = 'asignaturas del plan'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'curriculum_plan',
                    'course',
                ],
                name='unique_course_per_curriculum_plan',
            ),
            models.CheckConstraint(
                condition=models.Q(cycle__gte=1),
                name='curriculum_course_cycle_gte_1',
            ),
            models.CheckConstraint(
                condition=models.Q(credits__gte=0),
                name='curriculum_course_credits_gte_0',
            ),
            models.CheckConstraint(
                condition=models.Q(
                    prerequisite_credits__gte=0,
                    theory_hours__gte=0,
                    seminar_hours__gte=0,
                    theory_practice_hours__gte=0,
                    practice_hours__gte=0,
                    laboratory_hours__gte=0,
                ),
                name='curriculum_course_hours_and_prereq_gte_0',
            ),
            models.CheckConstraint(
                condition=models.Q(component__in=('A', 'B', 'C', 'D', 'E', 'F', 'G')),
                name='curriculum_course_component_valid',
            ),
        ]

    @property
    def theory_schedule_hours(self) -> Decimal:
        return (
            self.theory_hours
            + self.seminar_hours
            + self.theory_practice_hours
            + self.practice_hours
        )

    @property
    def has_laboratory(self) -> bool:
        return self.laboratory_hours > 0

    def clean(self) -> None:
        super().clean()

        if self.curriculum_plan_id is None or self.course_id is None:
            return

        plan_school_id = (
            CurriculumPlan.objects.filter(
                pk=self.curriculum_plan_id,
            )
            .values_list(
                'professional_school_id',
                flat=True,
            )
            .first()
        )
        course_school_id = (
            Course.objects.filter(
                pk=self.course_id,
            )
            .values_list(
                'professional_school_id',
                flat=True,
            )
            .first()
        )

        if (
            plan_school_id is not None
            and course_school_id is not None
            and plan_school_id != course_school_id
        ):
            raise ValidationError(
                {
                    'course': (
                        'La asignatura y el plan de estudios '
                        'deben pertenecer a la misma escuela '
                        'profesional.'
                    ),
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.curriculum_plan.code}: {self.course.code} — ciclo {self.cycle}'


class CurriculumCoursePrerequisite(models.Model):
    """Prerrequisito por asignatura dentro de una versión de la malla."""

    curriculum_course = models.ForeignKey(
        CurriculumCourse,
        on_delete=models.CASCADE,
        related_name='prerequisite_links',
    )
    prerequisite = models.ForeignKey(
        CurriculumCourse,
        on_delete=models.CASCADE,
        related_name='dependent_links',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            'curriculum_course_id',
            'prerequisite_id',
        ]
        verbose_name = 'prerrequisito de asignatura del plan'
        verbose_name_plural = 'prerrequisitos de asignaturas del plan'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'curriculum_course',
                    'prerequisite',
                ],
                name='unique_curriculum_course_prerequisite',
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    curriculum_course=models.F('prerequisite'),
                ),
                name='curriculum_course_prerequisite_not_self',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.curriculum_course_id is None or self.prerequisite_id is None:
            return

        if self.curriculum_course_id == self.prerequisite_id:
            raise ValidationError(
                {
                    'prerequisite': (
                        'Una asignatura no puede ser su propio prerrequisito.'
                    ),
                }
            )

        curriculum_plan_id = (
            CurriculumCourse.objects.filter(
                pk=self.curriculum_course_id,
            )
            .values_list(
                'curriculum_plan_id',
                flat=True,
            )
            .first()
        )
        prerequisite_plan_id = (
            CurriculumCourse.objects.filter(
                pk=self.prerequisite_id,
            )
            .values_list(
                'curriculum_plan_id',
                flat=True,
            )
            .first()
        )

        if (
            curriculum_plan_id is not None
            and prerequisite_plan_id is not None
            and curriculum_plan_id != prerequisite_plan_id
        ):
            raise ValidationError(
                {
                    'prerequisite': (
                        'El prerrequisito debe pertenecer al mismo plan de estudios.'
                    ),
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.curriculum_course} requiere {self.prerequisite.course.code}'
