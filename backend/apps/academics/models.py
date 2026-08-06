from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
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


class CurriculumCourse(models.Model):
    """Ubicación de una asignatura dentro de un plan de estudios."""

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
    cycle = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
    )
    credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
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
        ]

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
    """Grupo de una asignatura disponible en un periodo académico."""

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
    group_code = models.CharField(
        max_length=10,
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
            'group_code',
        ]
        verbose_name = 'oferta de asignatura'
        verbose_name_plural = 'ofertas de asignaturas'
        constraints = [
            models.UniqueConstraint(
                Lower('group_code'),
                'academic_period',
                'course',
                name='unique_course_group_per_period_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(group_code=''),
                name='course_offering_group_code_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.group_code = ' '.join(self.group_code.split()).upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f'{self.academic_period.code}: {self.course.code} — grupo {self.group_code}'
        )
