from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

from apps.academics.eligibility import evaluate_course_eligibility
from apps.academics.models import (
    AcademicPeriod,
    CourseOffering,
    CurriculumCourse,
    CurriculumPlan,
)


class CourseSection(models.Model):
    """Grupo de teoría o laboratorio perteneciente a una oferta."""

    class SectionType(models.TextChoices):
        THEORY = 'THEORY', 'Teoría'
        LABORATORY = 'LABORATORY', 'Laboratorio'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='sections',
    )
    section_type = models.CharField(
        max_length=10,
        choices=SectionType.choices,
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
            'course_offering_id',
            'section_type',
            'group_code',
        ]
        verbose_name = 'sección de horario'
        verbose_name_plural = 'secciones de horario'
        constraints = [
            models.UniqueConstraint(
                Lower('group_code'),
                'course_offering',
                'section_type',
                name='unique_section_group_per_offering_type_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(group_code=''),
                name='course_section_group_code_not_empty',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.course_offering_id is not None
            and self.section_type == self.SectionType.LABORATORY
            and not CourseOffering.objects.filter(
                pk=self.course_offering_id,
                curriculum_courses__laboratory_hours__gt=0,
            ).exists()
        ):
            raise ValidationError(
                {
                    'section_type': (
                        'La oferta no requiere una sección de laboratorio '
                        'según las entradas vinculadas de la malla.'
                    ),
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.group_code = ' '.join(self.group_code.split()).upper()
        self.full_clean()
        super().save(*args, **kwargs)

    def expected_hours_for(
        self,
        curriculum_course: CurriculumCourse,
    ) -> Decimal:
        if self.section_type == self.SectionType.THEORY:
            return curriculum_course.theory_schedule_hours

        return curriculum_course.laboratory_hours

    @property
    def expected_hours(self) -> Decimal | None:
        hour_values = {
            self.expected_hours_for(curriculum_course)
            for curriculum_course in self.course_offering.curriculum_courses.all()
        }

        if len(hour_values) != 1:
            return None

        return hour_values.pop()

    @property
    def scheduled_hours(self) -> Decimal:
        return sum(
            (meeting.duration_hours for meeting in self.meetings.all()),
            start=Decimal('0.00'),
        )

    def has_complete_hours_for(
        self,
        curriculum_course: CurriculumCourse,
    ) -> bool:
        return self.scheduled_hours == self.expected_hours_for(
            curriculum_course,
        )

    def __str__(self) -> str:
        return (
            f'{self.course_offering}: '
            f'{self.get_section_type_display()} {self.group_code}'
        )


class ClassMeeting(models.Model):
    """Reunión semanal de una sección de teoría o laboratorio."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Lunes'
        TUESDAY = 2, 'Martes'
        WEDNESDAY = 3, 'Miércoles'
        THURSDAY = 4, 'Jueves'
        FRIDAY = 5, 'Viernes'
        SATURDAY = 6, 'Sábado'
        SUNDAY = 7, 'Domingo'

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='meetings',
    )
    day_of_week = models.PositiveSmallIntegerField(
        choices=DayOfWeek.choices,
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(
        max_length=120,
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
            'day_of_week',
            'start_time',
            'end_time',
        ]
        verbose_name = 'reunión de clase'
        verbose_name_plural = 'reuniones de clase'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'section',
                    'day_of_week',
                    'start_time',
                    'end_time',
                ],
                name='unique_class_meeting_time_per_section',
            ),
            models.CheckConstraint(
                condition=models.Q(
                    start_time__lt=models.F('end_time'),
                ),
                name='class_meeting_start_before_end',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValidationError(
                {
                    'end_time': ('La hora de fin debe ser posterior a la de inicio.'),
                }
            )

    def save(self, *args, **kwargs) -> None:
        self.location = ' '.join(self.location.split())
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_hours(self) -> Decimal:
        start_seconds = (
            self.start_time.hour * 3600
            + self.start_time.minute * 60
            + self.start_time.second
        )
        end_seconds = (
            self.end_time.hour * 3600
            + self.end_time.minute * 60
            + self.end_time.second
        )

        return Decimal(end_seconds - start_seconds) / Decimal('3600')

    def __str__(self) -> str:
        return (
            f'{self.section} - {self.get_day_of_week_display()} '
            f'{self.start_time:%H:%M}-{self.end_time:%H:%M}'
        )


class ScheduleScenario(models.Model):
    """Escenario persistente de selección de horarios de un estudiante."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedule_scenarios',
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name='schedule_scenarios',
    )
    curriculum_plan = models.ForeignKey(
        CurriculumPlan,
        on_delete=models.PROTECT,
        related_name='schedule_scenarios',
    )
    name = models.CharField(
        max_length=100,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            '-updated_at',
            'name',
        ]
        verbose_name = 'escenario de horario'
        verbose_name_plural = 'escenarios de horario'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'user',
                'academic_period',
                'curriculum_plan',
                name='unique_schedule_scenario_name_ci',
            ),
            models.CheckConstraint(
                condition=~models.Q(name=''),
                name='schedule_scenario_name_not_empty',
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        self.name = ' '.join(self.name.split())
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} ({self.academic_period.code})'


class ScenarioSelection(models.Model):
    """Selección de teoría y laboratorio para una asignatura del escenario."""

    public_id = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
    )
    scenario = models.ForeignKey(
        ScheduleScenario,
        on_delete=models.CASCADE,
        related_name='selections',
    )
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='scenario_selections',
    )
    curriculum_course = models.ForeignKey(
        CurriculumCourse,
        on_delete=models.PROTECT,
        related_name='scenario_selections',
    )
    theory_section = models.ForeignKey(
        CourseSection,
        on_delete=models.PROTECT,
        related_name='theory_scenario_selections',
    )
    laboratory_section = models.ForeignKey(
        CourseSection,
        on_delete=models.PROTECT,
        related_name='laboratory_scenario_selections',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            'curriculum_course__cycle',
            'course_offering__course__code',
        ]
        verbose_name = 'selección de escenario'
        verbose_name_plural = 'selecciones de escenario'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'scenario',
                    'course_offering',
                ],
                name='unique_offering_per_schedule_scenario',
            ),
        ]

    def clean(self) -> None:
        super().clean()

        if not all(
            (
                self.scenario_id,
                self.course_offering_id,
                self.curriculum_course_id,
                self.theory_section_id,
            )
        ):
            return

        errors: dict[str, str] = {}

        if self.scenario.academic_period_id != self.course_offering.academic_period_id:
            errors['course_offering'] = (
                'La oferta debe pertenecer al periodo académico del escenario.'
            )

        if (
            self.curriculum_course.curriculum_plan_id
            != self.scenario.curriculum_plan_id
        ):
            errors['curriculum_course'] = (
                'La asignatura debe pertenecer al plan de estudios del escenario.'
            )
        elif not self.course_offering.curriculum_courses.filter(
            pk=self.curriculum_course_id,
        ).exists():
            errors['curriculum_course'] = (
                'La entrada de la malla no está vinculada a la oferta.'
            )

        if self.theory_section.course_offering_id != self.course_offering_id:
            errors['theory_section'] = (
                'La sección de teoría debe pertenecer a la oferta seleccionada.'
            )
        elif self.theory_section.section_type != CourseSection.SectionType.THEORY:
            errors['theory_section'] = 'Debes seleccionar una sección de teoría.'
        elif not self.theory_section.has_complete_hours_for(
            self.curriculum_course,
        ):
            errors['theory_section'] = (
                'La sección de teoría debe completar exactamente '
                f'{self.curriculum_course.theory_schedule_hours:.2f} horas; '
                f'actualmente tiene {self.theory_section.scheduled_hours:.2f}.'
            )

        laboratory_required = self.curriculum_course.laboratory_hours > 0

        if laboratory_required and self.laboratory_section_id is None:
            errors['laboratory_section'] = (
                'La asignatura requiere una sección de laboratorio.'
            )
        elif not laboratory_required and self.laboratory_section_id is not None:
            errors['laboratory_section'] = (
                'La asignatura no tiene horas de laboratorio en esta malla.'
            )
        elif self.laboratory_section_id is not None:
            if self.laboratory_section.course_offering_id != self.course_offering_id:
                errors['laboratory_section'] = (
                    'La sección de laboratorio debe pertenecer '
                    'a la oferta seleccionada.'
                )
            elif (
                self.laboratory_section.section_type
                != CourseSection.SectionType.LABORATORY
            ):
                errors['laboratory_section'] = (
                    'Debes seleccionar una sección de laboratorio.'
                )
            elif not self.laboratory_section.has_complete_hours_for(
                self.curriculum_course,
            ):
                errors['laboratory_section'] = (
                    'La sección de laboratorio debe completar exactamente '
                    f'{self.curriculum_course.laboratory_hours:.2f} horas; '
                    f'actualmente tiene '
                    f'{self.laboratory_section.scheduled_hours:.2f}.'
                )

        eligibility = evaluate_course_eligibility(
            self.scenario.user,
            self.curriculum_course,
        )

        if not eligibility.available:
            errors['curriculum_course'] = (
                'La asignatura está bloqueada: '
                f'{eligibility.blocking_message()}.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.scenario}: {self.course_offering.course.code}'
