from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from apps.academics.models import CourseOffering


class EvaluationScheme(models.Model):
    """Esquema de evaluación definido para una oferta académica."""

    PASSING_GRADE = Decimal('10.50')
    MAXIMUM_GRADE = Decimal('20.00')

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    course_offering = models.OneToOneField(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='evaluation_scheme',
    )
    passing_grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=PASSING_GRADE,
        validators=[
            MinValueValidator(PASSING_GRADE),
            MaxValueValidator(PASSING_GRADE),
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
            '-course_offering__academic_period__year',
            'course_offering__academic_period__term',
            'course_offering__course__code',
        ]
        verbose_name = 'esquema de evaluación'
        verbose_name_plural = 'esquemas de evaluación'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(passing_grade=Decimal('10.50')),
                name='evaluation_scheme_passing_grade_exact',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Esquema de {self.course_offering}'


class EvaluationComponent(models.Model):
    """Componente ponderado o examen sustitutorio de un esquema."""

    class ComponentType(models.TextChoices):
        EXAM_1 = 'EXAM_1', 'Examen 1'
        EXAM_2 = 'EXAM_2', 'Examen 2'
        SUBSTITUTE = 'SUBSTITUTE', 'Sustitutorio'
        OTHER = 'OTHER', 'Otro componente'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    scheme = models.ForeignKey(
        EvaluationScheme,
        on_delete=models.CASCADE,
        related_name='components',
    )
    name = models.CharField(
        max_length=100,
    )
    component_type = models.CharField(
        max_length=10,
        choices=ComponentType.choices,
        default=ComponentType.OTHER,
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0')),
            MaxValueValidator(Decimal('100')),
        ],
    )
    order = models.PositiveSmallIntegerField(
        default=0,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            'scheme_id',
            'order',
            'name',
        ]
        verbose_name = 'componente de evaluación'
        verbose_name_plural = 'componentes de evaluación'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'scheme',
                name='unique_evaluation_component_name_ci',
            ),
            models.UniqueConstraint(
                fields=[
                    'scheme',
                    'component_type',
                ],
                condition=~models.Q(component_type='OTHER'),
                name='unique_special_component_type_per_scheme',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        component_type='SUBSTITUTE',
                        weight=0,
                    )
                    | models.Q(
                        weight__gt=0,
                        weight__lte=100,
                    )
                    & ~models.Q(component_type='SUBSTITUTE')
                ),
                name='evaluation_component_weight_by_type',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='evaluation_component_name_not_empty',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if self.weight is None:
            return

        if (
            self.component_type == self.ComponentType.SUBSTITUTE
            and self.weight != 0
        ):
            raise ValidationError(
                {
                    'weight': ('El sustitutorio debe tener peso 0.'),
                }
            )

        if (
            self.component_type != self.ComponentType.SUBSTITUTE
            and self.weight <= 0
        ):
            raise ValidationError(
                {
                    'weight': ('Un componente evaluativo debe tener peso positivo.'),
                }
            )

    def save(self, *args, **kwargs) -> None:
        if self.name:
            self.name = ' '.join(self.name.split())
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.scheme}: {self.name}'
