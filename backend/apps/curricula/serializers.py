from decimal import Decimal

from rest_framework import serializers

from apps.institution.models import ProfessionalSchool

from .models import (
    AcademicTerm,
    Course,
    CurriculumPlan,
    ElectiveBranch,
    EvaluationComponent,
    Instructor,
    Prerequisite,
    Syllabus,
)


class CurriculumPlanSerializer(serializers.ModelSerializer):
    school = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.filter(is_active=True),
    )

    class Meta:
        model = CurriculumPlan
        fields = ['public_id', 'school', 'year', 'name', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    curriculum_plan = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=CurriculumPlan.objects.filter(is_active=True),
    )
    branch = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=ElectiveBranch.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    has_lab = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'public_id',
            'curriculum_plan',
            'code',
            'name',
            'credits',
            'theory_hours',
            'practice_hours',
            'seminar_hours',
            'theory_practice_hours',
            'lab_hours',
            'cycle',
            'course_type',
            'academic_area',
            'branch',
            'min_credits_required',
            'has_lab',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['public_id', 'created_at']

    def validate(self, attrs):
        branch = attrs.get('branch')
        course_type = attrs.get('course_type', getattr(self.instance, 'course_type', None))
        if branch and course_type != Course.CourseType.ELECTIVE:
            raise serializers.ValidationError(
                'Solo un curso electivo puede pertenecer a una rama electiva.',
            )
        return attrs


class ElectiveBranchSerializer(serializers.ModelSerializer):
    curriculum_plan = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=CurriculumPlan.objects.filter(is_active=True),
    )

    class Meta:
        model = ElectiveBranch
        fields = ['public_id', 'curriculum_plan', 'name', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class PrerequisiteSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='public_id', queryset=Course.objects.all())
    required_course = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Course.objects.all(),
    )

    class Meta:
        model = Prerequisite
        fields = ['public_id', 'course', 'required_course', 'created_at']
        read_only_fields = ['public_id', 'created_at']

    def validate(self, attrs):
        course = attrs['course']
        required_course = attrs['required_course']
        if course == required_course:
            raise serializers.ValidationError(
                'Un curso no puede ser prerrequisito de sí mismo.',
            )
        if course.curriculum_plan_id != required_course.curriculum_plan_id:
            raise serializers.ValidationError(
                'El curso y su prerrequisito deben pertenecer al mismo plan curricular.',
            )
        return attrs


class AcademicTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicTerm
        fields = ['public_id', 'code', 'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['public_id', 'full_name', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class EvaluationComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationComponent
        fields = ['public_id', 'name', 'weight', 'order']
        read_only_fields = ['public_id']


class SyllabusSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='public_id', queryset=Course.objects.all())
    academic_term = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=AcademicTerm.objects.filter(is_active=True),
    )
    instructors = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Instructor.objects.filter(is_active=True),
        many=True,
    )
    evaluation_components = EvaluationComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Syllabus
        fields = [
            'public_id',
            'course',
            'academic_term',
            'instructors',
            'pdf_url',
            'description',
            'competencies',
            'thematic_content',
            'methodology',
            'evaluation_criteria',
            'weekly_plan',
            'bibliography',
            'resources',
            'lab_practice_info',
            'institutional_references',
            'evaluation_components',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['public_id', 'evaluation_components', 'created_at']


def validate_component_weights_sum_to_100(components_data):
    """Standalone validator, used by the evaluation-components-bulk-set
    action on SyllabusViewSet: the weights of a syllabus's components
    must add up to 100."""

    total = sum((Decimal(str(c['weight'])) for c in components_data), Decimal('0'))
    if total != Decimal('100'):
        raise serializers.ValidationError(
            f'La suma de los pesos debe ser 100 (actual: {total}).',
        )
