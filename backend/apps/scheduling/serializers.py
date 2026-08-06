from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.academics.eligibility import evaluate_course_eligibility
from apps.academics.models import (
    AcademicPeriod,
    CourseOffering,
    CurriculumCourse,
    CurriculumPlan,
)
from apps.academics.serializers import (
    AcademicPeriodSerializer,
    CurriculumPlanCatalogSerializer,
    SchoolScopedWriteSerializerMixin,
)

from .models import (
    ClassMeeting,
    CourseSection,
    ScenarioSelection,
    ScheduleScenario,
)


class ClassMeetingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    day_label = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True,
    )

    class Meta:
        model = ClassMeeting
        fields = [
            'id',
            'day_of_week',
            'day_label',
            'start_time',
            'end_time',
            'location',
        ]
        read_only_fields = fields


class CourseSectionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    course_offering_id = serializers.UUIDField(
        source='course_offering.public_id',
        read_only=True,
    )
    academic_period_code = serializers.CharField(
        source='course_offering.academic_period.code',
        read_only=True,
    )
    course_code = serializers.CharField(
        source='course_offering.course.code',
        read_only=True,
    )
    course_name = serializers.CharField(
        source='course_offering.course.name',
        read_only=True,
    )
    section_type_label = serializers.CharField(
        source='get_section_type_display',
        read_only=True,
    )
    expected_hours = serializers.SerializerMethodField()
    scheduled_hours = serializers.SerializerMethodField()
    hours_complete = serializers.SerializerMethodField()
    meetings = ClassMeetingSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CourseSection
        fields = [
            'id',
            'course_offering_id',
            'academic_period_code',
            'course_code',
            'course_name',
            'section_type',
            'section_type_label',
            'group_code',
            'is_active',
            'expected_hours',
            'scheduled_hours',
            'hours_complete',
            'meetings',
        ]
        read_only_fields = fields

    def get_expected_hours(self, obj: CourseSection) -> str | None:
        expected_hours = obj.expected_hours

        if expected_hours is None:
            return None

        return f'{expected_hours:.2f}'

    def get_scheduled_hours(self, obj: CourseSection) -> str:
        return f'{obj.scheduled_hours:.2f}'

    def get_hours_complete(self, obj: CourseSection) -> bool:
        expected_hours = obj.expected_hours

        return expected_hours is not None and obj.scheduled_hours == expected_hours


class CourseSectionWriteSerializer(
    SchoolScopedWriteSerializerMixin,
    serializers.ModelSerializer,
):
    school_scoped_fields = {
        'course_offering_id': 'course__professional_school_id',
    }
    course_offering_id = serializers.SlugRelatedField(
        source='course_offering',
        slug_field='public_id',
        queryset=CourseOffering.objects.all(),
        write_only=True,
    )

    class Meta:
        model = CourseSection
        fields = [
            'course_offering_id',
            'section_type',
            'group_code',
            'is_active',
        ]
        validators = []
        extra_kwargs = {
            'is_active': {
                'required': False,
            },
        }

    def validate_group_code(self, value: str) -> str:
        normalized_code = ' '.join(value.split()).upper()

        if not normalized_code:
            raise serializers.ValidationError('El código del grupo es obligatorio.')

        return normalized_code

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        offering = attrs.get('course_offering')
        section_type = attrs.get('section_type')
        group_code = attrs.get('group_code')

        if self.instance is not None:
            if (
                isinstance(offering, CourseOffering)
                and offering.pk != self.instance.course_offering_id
            ):
                raise serializers.ValidationError(
                    {
                        'course_offering_id': (
                            'No se puede cambiar la oferta de una sección existente.'
                        ),
                    }
                )

            if section_type is not None and section_type != self.instance.section_type:
                raise serializers.ValidationError(
                    {
                        'section_type': (
                            'No se puede cambiar el tipo de una sección existente.'
                        ),
                    }
                )

            offering = self.instance.course_offering
            section_type = self.instance.section_type
            group_code = group_code or self.instance.group_code

        if (
            isinstance(offering, CourseOffering)
            and section_type == CourseSection.SectionType.LABORATORY
            and not offering.curriculum_courses.filter(
                laboratory_hours__gt=0,
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    'section_type': (
                        'La oferta no requiere una sección de laboratorio.'
                    ),
                }
            )

        if (
            isinstance(offering, CourseOffering)
            and isinstance(section_type, str)
            and isinstance(group_code, str)
        ):
            existing_sections = CourseSection.objects.filter(
                course_offering=offering,
                section_type=section_type,
                group_code__iexact=group_code,
            )

            if self.instance is not None:
                existing_sections = existing_sections.exclude(
                    pk=self.instance.pk,
                )

            if existing_sections.exists():
                raise serializers.ValidationError(
                    {
                        'group_code': (
                            'Ya existe este grupo para el tipo y la oferta.'
                        ),
                    }
                )

        return attrs

    def create(self, validated_data: dict[str, object]) -> CourseSection:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'group_code': ('Ya existe este grupo para el tipo y la oferta.'),
                }
            ) from error


class ClassMeetingWriteSerializer(
    SchoolScopedWriteSerializerMixin,
    serializers.ModelSerializer,
):
    school_scoped_fields = {
        'section_id': 'course_offering__course__professional_school_id',
    }
    section_id = serializers.SlugRelatedField(
        source='section',
        slug_field='public_id',
        queryset=CourseSection.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ClassMeeting
        fields = [
            'section_id',
            'day_of_week',
            'start_time',
            'end_time',
            'location',
        ]
        validators = []
        extra_kwargs = {
            'location': {
                'required': False,
            },
        }

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        section = attrs.get('section')
        day_of_week = attrs.get('day_of_week')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if self.instance is not None:
            if (
                isinstance(section, CourseSection)
                and section.pk != self.instance.section_id
            ):
                raise serializers.ValidationError(
                    {
                        'section_id': (
                            'No se puede cambiar la sección de una reunión existente.'
                        ),
                    }
                )

            section = self.instance.section
            if day_of_week is None:
                day_of_week = self.instance.day_of_week

            if start_time is None:
                start_time = self.instance.start_time

            if end_time is None:
                end_time = self.instance.end_time

        if start_time is not None and end_time is not None and start_time >= end_time:
            raise serializers.ValidationError(
                {
                    'end_time': ('La hora de fin debe ser posterior a la de inicio.'),
                }
            )

        if (
            isinstance(section, CourseSection)
            and isinstance(day_of_week, int)
            and start_time is not None
            and end_time is not None
        ):
            duplicate_meetings = ClassMeeting.objects.filter(
                section=section,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )

            if self.instance is not None:
                duplicate_meetings = duplicate_meetings.exclude(
                    pk=self.instance.pk,
                )

            if duplicate_meetings.exists():
                raise serializers.ValidationError(
                    {
                        'non_field_errors': [
                            (
                                'Ya existe una reunión con la misma sección, '
                                'día y horario.'
                            ),
                        ],
                    }
                )

            other_meetings = section.meetings.all()

            if self.instance is not None:
                other_meetings = other_meetings.exclude(
                    pk=self.instance.pk,
                )

            candidate = ClassMeeting(
                section=section,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
            )
            scheduled_hours = sum(
                (meeting.duration_hours for meeting in other_meetings),
                start=candidate.duration_hours,
            )
            expected_hours = section.expected_hours

            if expected_hours is None:
                raise serializers.ValidationError(
                    {
                        'section_id': (
                            'La oferta tiene versiones de malla con cargas '
                            'horarias incompatibles.'
                        ),
                    }
                )

            if scheduled_hours > expected_hours:
                raise serializers.ValidationError(
                    {
                        'end_time': (
                            'La suma de reuniones excedería las horas definidas '
                            f'en la malla ({expected_hours:.2f}).'
                        ),
                    }
                )

        return attrs


class ScheduleScenarioWriteSerializer(serializers.ModelSerializer):
    academic_period_id = serializers.SlugRelatedField(
        source='academic_period',
        slug_field='public_id',
        queryset=AcademicPeriod.objects.filter(is_active=True),
        write_only=True,
    )
    curriculum_plan_id = serializers.SlugRelatedField(
        source='curriculum_plan',
        slug_field='public_id',
        queryset=CurriculumPlan.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta:
        model = ScheduleScenario
        fields = [
            'academic_period_id',
            'curriculum_plan_id',
            'name',
        ]
        validators = []

    def validate_name(self, value: str) -> str:
        normalized_name = ' '.join(value.split())

        if not normalized_name:
            raise serializers.ValidationError('El nombre del escenario es obligatorio.')

        return normalized_name

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        period = attrs.get('academic_period')
        plan = attrs.get('curriculum_plan')
        name = attrs.get('name')
        user = self.context['request'].user

        if self.instance is not None:
            if (
                isinstance(period, AcademicPeriod)
                and period.pk != self.instance.academic_period_id
            ):
                raise serializers.ValidationError(
                    {
                        'academic_period_id': (
                            'No se puede cambiar el periodo de un escenario existente.'
                        ),
                    }
                )

            if (
                isinstance(plan, CurriculumPlan)
                and plan.pk != self.instance.curriculum_plan_id
            ):
                raise serializers.ValidationError(
                    {
                        'curriculum_plan_id': (
                            'No se puede cambiar el plan de un escenario existente.'
                        ),
                    }
                )

            period = self.instance.academic_period
            plan = self.instance.curriculum_plan
            name = name or self.instance.name

        if (
            isinstance(period, AcademicPeriod)
            and isinstance(plan, CurriculumPlan)
            and isinstance(name, str)
        ):
            existing = ScheduleScenario.objects.filter(
                user=user,
                academic_period=period,
                curriculum_plan=plan,
                name__iexact=name,
            )

            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    {
                        'name': ('Ya existe un escenario con este nombre.'),
                    }
                )

        return attrs

    def create(self, validated_data: dict[str, object]) -> ScheduleScenario:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ScenarioSelectionWriteSerializer(serializers.ModelSerializer):
    course_offering_id = serializers.SlugRelatedField(
        source='course_offering',
        slug_field='public_id',
        queryset=CourseOffering.objects.filter(is_active=True),
        write_only=True,
    )
    curriculum_course_id = serializers.SlugRelatedField(
        source='curriculum_course',
        slug_field='public_id',
        queryset=CurriculumCourse.objects.all(),
        write_only=True,
    )
    theory_section_id = serializers.SlugRelatedField(
        source='theory_section',
        slug_field='public_id',
        queryset=CourseSection.objects.filter(
            is_active=True,
            section_type=CourseSection.SectionType.THEORY,
        ),
        write_only=True,
    )
    laboratory_section_id = serializers.SlugRelatedField(
        source='laboratory_section',
        slug_field='public_id',
        queryset=CourseSection.objects.filter(
            is_active=True,
            section_type=CourseSection.SectionType.LABORATORY,
        ),
        allow_null=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = ScenarioSelection
        fields = [
            'course_offering_id',
            'curriculum_course_id',
            'theory_section_id',
            'laboratory_section_id',
        ]
        validators = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        scenario = self.context.get('scenario')

        if not isinstance(scenario, ScheduleScenario):
            return

        self.fields['course_offering_id'].queryset = (
            CourseOffering.objects.filter(
                is_active=True,
                academic_period=scenario.academic_period,
                curriculum_courses__curriculum_plan=scenario.curriculum_plan,
            ).distinct()
        )
        self.fields['curriculum_course_id'].queryset = (
            CurriculumCourse.objects.filter(
                curriculum_plan=scenario.curriculum_plan,
            )
        )
        section_queryset = CourseSection.objects.filter(
            is_active=True,
            course_offering__is_active=True,
            course_offering__academic_period=scenario.academic_period,
            course_offering__curriculum_courses__curriculum_plan=(
                scenario.curriculum_plan
            ),
        ).distinct()
        self.fields['theory_section_id'].queryset = section_queryset.filter(
            section_type=CourseSection.SectionType.THEORY,
        )
        self.fields['laboratory_section_id'].queryset = section_queryset.filter(
            section_type=CourseSection.SectionType.LABORATORY,
        )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        scenario = self.context['scenario']
        offering = attrs.get('course_offering')
        curriculum_course = attrs.get('curriculum_course')
        theory_section = attrs.get('theory_section')
        laboratory_section = attrs.get('laboratory_section')

        if self.instance is not None:
            immutable_errors = {}

            if (
                isinstance(offering, CourseOffering)
                and offering.pk != self.instance.course_offering_id
            ):
                immutable_errors['course_offering_id'] = (
                    'No se puede cambiar la oferta de una selección existente.'
                )

            if (
                isinstance(curriculum_course, CurriculumCourse)
                and curriculum_course.pk != self.instance.curriculum_course_id
            ):
                immutable_errors['curriculum_course_id'] = (
                    'No se puede cambiar la entrada de malla '
                    'de una selección existente.'
                )

            if immutable_errors:
                raise serializers.ValidationError(immutable_errors)

            offering = self.instance.course_offering
            curriculum_course = self.instance.curriculum_course
            theory_section = theory_section or self.instance.theory_section

            if 'laboratory_section' not in attrs:
                laboratory_section = self.instance.laboratory_section

        errors = {}

        if (
            isinstance(offering, CourseOffering)
            and isinstance(curriculum_course, CurriculumCourse)
            and not offering.curriculum_courses.filter(
                pk=curriculum_course.pk,
            ).exists()
        ):
            errors['curriculum_course_id'] = (
                'La entrada de malla no está vinculada a la oferta.'
            )

        if isinstance(offering, CourseOffering) and isinstance(
            theory_section,
            CourseSection,
        ):
            if theory_section.course_offering_id != offering.pk:
                errors['theory_section_id'] = (
                    'La sección de teoría no pertenece a la oferta.'
                )
            elif (
                isinstance(curriculum_course, CurriculumCourse)
                and not theory_section.has_complete_hours_for(
                    curriculum_course,
                )
            ):
                errors['theory_section_id'] = (
                    'La sección de teoría debe completar exactamente '
                    f'{curriculum_course.theory_schedule_hours:.2f} horas; '
                    f'actualmente tiene {theory_section.scheduled_hours:.2f}.'
                )

        if isinstance(curriculum_course, CurriculumCourse):
            laboratory_required = curriculum_course.laboratory_hours > 0

            if laboratory_required and laboratory_section is None:
                errors['laboratory_section_id'] = (
                    'La asignatura requiere una sección de laboratorio.'
                )
            elif not laboratory_required and laboratory_section is not None:
                errors['laboratory_section_id'] = (
                    'La asignatura no tiene horas de laboratorio.'
                )

        if isinstance(offering, CourseOffering) and isinstance(
            laboratory_section,
            CourseSection,
        ):
            if laboratory_section.course_offering_id != offering.pk:
                errors['laboratory_section_id'] = (
                    'La sección de laboratorio no pertenece a la oferta.'
                )
            elif (
                isinstance(curriculum_course, CurriculumCourse)
                and not laboratory_section.has_complete_hours_for(
                    curriculum_course,
                )
            ):
                errors['laboratory_section_id'] = (
                    'La sección de laboratorio debe completar exactamente '
                    f'{curriculum_course.laboratory_hours:.2f} horas; '
                    f'actualmente tiene {laboratory_section.scheduled_hours:.2f}.'
                )

        if isinstance(offering, CourseOffering):
            existing = ScenarioSelection.objects.filter(
                scenario=scenario,
                course_offering=offering,
            )

            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                errors['course_offering_id'] = (
                    'La oferta ya está seleccionada en este escenario.'
                )

        if isinstance(curriculum_course, CurriculumCourse):
            eligibility = evaluate_course_eligibility(
                scenario.user,
                curriculum_course,
            )

            if not eligibility.available:
                errors.setdefault(
                    'curriculum_course_id',
                    'La asignatura está bloqueada: '
                    f'{eligibility.blocking_message()}.',
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data: dict[str, object]) -> ScenarioSelection:
        validated_data['scenario'] = self.context['scenario']
        return super().create(validated_data)


class ScenarioSelectionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    course_offering_id = serializers.UUIDField(
        source='course_offering.public_id',
        read_only=True,
    )
    curriculum_course_id = serializers.UUIDField(
        source='curriculum_course.public_id',
        read_only=True,
    )
    course_code = serializers.CharField(
        source='course_offering.course.code',
        read_only=True,
    )
    course_name = serializers.CharField(
        source='course_offering.course.name',
        read_only=True,
    )
    theory_section = CourseSectionSerializer(read_only=True)
    laboratory_section = CourseSectionSerializer(read_only=True)

    class Meta:
        model = ScenarioSelection
        fields = [
            'id',
            'course_offering_id',
            'curriculum_course_id',
            'course_code',
            'course_name',
            'theory_section',
            'laboratory_section',
        ]
        read_only_fields = fields


class ScheduleScenarioSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    academic_period = AcademicPeriodSerializer(read_only=True)
    curriculum_plan = CurriculumPlanCatalogSerializer(read_only=True)
    selections = ScenarioSelectionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ScheduleScenario
        fields = [
            'id',
            'name',
            'academic_period',
            'curriculum_plan',
            'selections',
        ]
        read_only_fields = fields


class AvailableSectionQuerySerializer(serializers.Serializer):
    academic_period = serializers.UUIDField(required=False)
    curriculum_plan = serializers.UUIDField(required=False)


class CourseEligibilityQuerySerializer(serializers.Serializer):
    academic_period = serializers.UUIDField()
    curriculum_plan = serializers.UUIDField()


class CourseEligibilitySerializer(serializers.Serializer):
    course_offering_id = serializers.UUIDField()
    curriculum_course_id = serializers.UUIDField()
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    available = serializers.BooleanField()
    approved_credits = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
    required_credits = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
    credits_met = serializers.BooleanField()
    missing_prerequisites = serializers.ListField()


class ScheduleConflictSerializer(serializers.Serializer):
    first_meeting_id = serializers.UUIDField()
    first_section_id = serializers.UUIDField()
    first_course_code = serializers.CharField()
    second_meeting_id = serializers.UUIDField()
    second_section_id = serializers.UUIDField()
    second_course_code = serializers.CharField()
    day_of_week = serializers.IntegerField()
    day_label = serializers.CharField()
    overlap_start = serializers.TimeField()
    overlap_end = serializers.TimeField()
