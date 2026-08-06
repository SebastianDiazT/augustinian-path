from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.academics.models import CourseOffering, CurriculumCourse
from apps.academics.serializers import SchoolScopedWriteSerializerMixin
from apps.grading.models import EvaluationScheme
from apps.grading.serializers import EvaluationSchemeSerializer

from .models import Syllabus


def _json_safe(value: object) -> object:
    if isinstance(value, Decimal):
        return f'{value:.2f}'

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, list):
        return [_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {
            key: _json_safe(item)
            for key, item in value.items()
        }

    return value


class SyllabusInstructorInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    academic_degree = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        default='',
    )
    academic_department = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default='',
    )
    weekly_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
    )
    schedule = serializers.ListField(
        child=serializers.CharField(max_length=120),
        allow_empty=True,
    )


class SyllabusCompetencyInputSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        default='',
    )
    description = serializers.CharField()


class SyllabusTopicInputSerializer(serializers.Serializer):
    number = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=500)


class SyllabusChapterInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    topics = SyllabusTopicInputSerializer(
        many=True,
        allow_empty=False,
    )


class SyllabusUnitInputSerializer(serializers.Serializer):
    order = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=200)
    chapters = SyllabusChapterInputSerializer(
        many=True,
        allow_empty=False,
    )


class SyllabusWeekInputSerializer(serializers.Serializer):
    week = serializers.IntegerField(min_value=1, max_value=52)
    topic = serializers.CharField(max_length=500)
    instructor = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default='',
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
    )
    cumulative_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
    )


class SyllabusEvaluationInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    evaluation_date = serializers.DateField()
    theory_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
    )
    continuous_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
    )
    total_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
    )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if attrs['total_weight'] != (
            attrs['theory_weight'] + attrs['continuous_weight']
        ):
            raise serializers.ValidationError(
                {
                    'total_weight': (
                        'El total debe ser la suma de evaluación teórica '
                        'y continua.'
                    ),
                }
            )

        return attrs


class SyllabusBibliographyInputSerializer(serializers.Serializer):
    class Category:
        BASIC = 'BASIC'
        CONSULTATION = 'CONSULTATION'

    category = serializers.ChoiceField(
        choices=[
            Category.BASIC,
            Category.CONSULTATION,
        ],
    )
    citation = serializers.CharField()
    url = serializers.URLField(
        required=False,
        allow_blank=True,
        default='',
    )


class SyllabusSerializer(serializers.ModelSerializer):
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
    academic_period_code = serializers.CharField(
        source='course_offering.academic_period.code',
        read_only=True,
    )
    professional_school = serializers.CharField(
        source='course_offering.course.professional_school.name',
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
    cycle = serializers.IntegerField(
        source='curriculum_course.cycle',
        read_only=True,
    )
    credits = serializers.DecimalField(
        source='curriculum_course.credits',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    prerequisite_credits = serializers.DecimalField(
        source='curriculum_course.prerequisite_credits',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    theory_hours = serializers.DecimalField(
        source='curriculum_course.theory_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    seminar_hours = serializers.DecimalField(
        source='curriculum_course.seminar_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    theory_practice_hours = serializers.DecimalField(
        source='curriculum_course.theory_practice_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    practice_hours = serializers.DecimalField(
        source='curriculum_course.practice_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    theory_schedule_hours = serializers.DecimalField(
        source='curriculum_course.theory_schedule_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    laboratory_hours = serializers.DecimalField(
        source='curriculum_course.laboratory_hours',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    prerequisites = serializers.SerializerMethodField()
    evaluation_scheme = serializers.SerializerMethodField()
    status_label = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )

    class Meta:
        model = Syllabus
        fields = [
            'id',
            'course_offering_id',
            'curriculum_course_id',
            'academic_period_code',
            'professional_school',
            'course_code',
            'course_name',
            'cycle',
            'duration_weeks',
            'credits',
            'prerequisite_credits',
            'theory_hours',
            'seminar_hours',
            'theory_practice_hours',
            'practice_hours',
            'theory_schedule_hours',
            'laboratory_hours',
            'prerequisites',
            'status',
            'status_label',
            'publication_date',
            'foundation',
            'instructors',
            'competencies',
            'thematic_content',
            'teaching_methods',
            'teaching_media',
            'organization_forms',
            'formative_research',
            'social_responsibility',
            'weekly_schedule',
            'evaluation_strategy',
            'evaluation_schedule',
            'evaluation_scheme',
            'approval_requirements',
            'bibliography',
            'source_document_url',
        ]
        read_only_fields = fields

    @extend_schema_field(
        serializers.ListField(child=serializers.DictField()),
    )
    def get_prerequisites(self, obj: Syllabus) -> list[dict[str, object]]:
        return [
            {
                'curriculum_course_id': str(prerequisite.public_id),
                'course_code': prerequisite.course.code,
                'course_name': prerequisite.course.name,
            }
            for prerequisite in obj.curriculum_course.prerequisites.all()
        ]

    @extend_schema_field(EvaluationSchemeSerializer(allow_null=True))
    def get_evaluation_scheme(self, obj: Syllabus) -> dict[str, object] | None:
        try:
            scheme = obj.course_offering.evaluation_scheme
        except EvaluationScheme.DoesNotExist:
            return None

        return EvaluationSchemeSerializer(scheme).data


class SyllabusWriteSerializer(
    SchoolScopedWriteSerializerMixin,
    serializers.ModelSerializer,
):
    school_scoped_fields = {
        'course_offering_id': 'course__professional_school_id',
        'curriculum_course_id': 'curriculum_plan__professional_school_id',
    }
    course_offering_id = serializers.SlugRelatedField(
        source='course_offering',
        slug_field='public_id',
        queryset=CourseOffering.objects.all(),
        write_only=True,
    )
    curriculum_course_id = serializers.SlugRelatedField(
        source='curriculum_course',
        slug_field='public_id',
        queryset=CurriculumCourse.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Syllabus
        fields = [
            'course_offering_id',
            'curriculum_course_id',
            'status',
            'duration_weeks',
            'publication_date',
            'foundation',
            'instructors',
            'competencies',
            'thematic_content',
            'teaching_methods',
            'teaching_media',
            'organization_forms',
            'formative_research',
            'social_responsibility',
            'weekly_schedule',
            'evaluation_strategy',
            'evaluation_schedule',
            'approval_requirements',
            'bibliography',
            'source_document_url',
        ]
        validators = []

    def _validate_list(
        self,
        value: object,
        serializer_class: type[serializers.Serializer],
    ) -> list[object]:
        serializer = serializer_class(
            data=value,
            many=True,
        )
        serializer.is_valid(raise_exception=True)

        return _json_safe(serializer.validated_data)

    def validate_instructors(self, value: object) -> list[object]:
        return self._validate_list(value, SyllabusInstructorInputSerializer)

    def validate_competencies(self, value: object) -> list[object]:
        validated = self._validate_list(
            value,
            SyllabusCompetencyInputSerializer,
        )
        codes = [item['code'] for item in validated if item['code']]

        if len(codes) != len(set(codes)):
            raise serializers.ValidationError(
                'No se puede repetir el código de una competencia.'
            )

        return validated

    def validate_thematic_content(self, value: object) -> list[object]:
        validated = self._validate_list(
            value,
            SyllabusUnitInputSerializer,
        )
        unit_orders = [item['order'] for item in validated]

        if len(unit_orders) != len(set(unit_orders)):
            raise serializers.ValidationError(
                'No se puede repetir el orden de una unidad.'
            )

        return validated

    def validate_weekly_schedule(self, value: object) -> list[object]:
        validated = self._validate_list(
            value,
            SyllabusWeekInputSerializer,
        )
        weeks = [item['week'] for item in validated]

        if weeks != sorted(weeks):
            raise serializers.ValidationError(
                'El cronograma debe estar ordenado por semana.'
            )

        if len(weeks) != len(set(weeks)):
            raise serializers.ValidationError(
                'No se puede repetir una semana.'
            )

        cumulative_values = [
            Decimal(item['cumulative_percentage'])
            for item in validated
        ]

        if cumulative_values != sorted(cumulative_values):
            raise serializers.ValidationError(
                'El porcentaje acumulado no puede disminuir.'
            )

        return validated

    def validate_evaluation_schedule(self, value: object) -> list[object]:
        validated = self._validate_list(
            value,
            SyllabusEvaluationInputSerializer,
        )
        total_weight = sum(
            (Decimal(item['total_weight']) for item in validated),
            start=Decimal('0.00'),
        )

        if validated and total_weight != Decimal('100.00'):
            raise serializers.ValidationError(
                'La ponderación total del cronograma debe sumar 100.00%.'
            )

        return validated

    def validate_bibliography(self, value: object) -> list[object]:
        return self._validate_list(
            value,
            SyllabusBibliographyInputSerializer,
        )

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        offering = attrs.get('course_offering')
        curriculum_course = attrs.get('curriculum_course')

        if self.instance is not None:
            immutable_errors = {}

            if (
                isinstance(offering, CourseOffering)
                and offering.pk != self.instance.course_offering_id
            ):
                immutable_errors['course_offering_id'] = (
                    'No se puede cambiar la oferta de un sílabo existente.'
                )

            if (
                isinstance(curriculum_course, CurriculumCourse)
                and curriculum_course.pk != self.instance.curriculum_course_id
            ):
                immutable_errors['curriculum_course_id'] = (
                    'No se puede cambiar la entrada de malla de un sílabo existente.'
                )

            if immutable_errors:
                raise serializers.ValidationError(immutable_errors)

            offering = self.instance.course_offering
            curriculum_course = self.instance.curriculum_course

        if (
            isinstance(offering, CourseOffering)
            and isinstance(curriculum_course, CurriculumCourse)
            and not offering.curriculum_courses.filter(
                pk=curriculum_course.pk,
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    'curriculum_course_id': (
                        'La entrada de malla no está vinculada a la oferta.'
                    ),
                }
            )

        self._validate_publication(attrs)

        return attrs

    def _validate_publication(self, attrs: dict[str, object]) -> None:
        status_value = attrs.get(
            'status',
            (
                self.instance.status
                if self.instance is not None
                else Syllabus.Status.DRAFT
            ),
        )

        if status_value != Syllabus.Status.PUBLISHED:
            return

        duration_weeks = attrs.get(
            'duration_weeks',
            self.instance.duration_weeks if self.instance is not None else 17,
        )
        weekly_schedule = attrs.get(
            'weekly_schedule',
            self.instance.weekly_schedule if self.instance is not None else [],
        )
        expected_weeks = list(range(1, duration_weeks + 1))
        actual_weeks = [item['week'] for item in weekly_schedule]

        if actual_weeks != expected_weeks:
            raise serializers.ValidationError(
                {
                    'weekly_schedule': (
                        'Un sílabo publicado debe programar consecutivamente '
                        f'las {duration_weeks} semanas.'
                    ),
                }
            )

        if Decimal(weekly_schedule[-1]['cumulative_percentage']) != Decimal(
            '100.00'
        ):
            raise serializers.ValidationError(
                {
                    'weekly_schedule': (
                        'El porcentaje acumulado final debe ser 100.00%.'
                    ),
                }
            )

    def create(self, validated_data: dict[str, object]) -> Syllabus:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'course_offering_id': (
                        'Ya existe un sílabo para esta oferta y entrada de malla.'
                    ),
                }
            ) from error
