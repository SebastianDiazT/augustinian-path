from rest_framework import serializers

from apps.institution.models import ProfessionalSchool

from .models import Course, CurriculumPlan, ElectiveBranch, Prerequisite


class CurriculumPlanCatalogSerializer(serializers.ModelSerializer):
    """Para llenar el último dropdown del Onboarding del alumno."""

    class Meta:
        model = CurriculumPlan
        fields = ['public_id', 'name', 'year']


class CourseMeshSerializer(serializers.ModelSerializer):
    """El motor de React Flow: Devuelve el curso y con quién se conecta."""

    prerequisite_ids = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.name', read_only=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'public_id',
            'code',
            'name',
            'credits',
            'cycle',
            'course_type',
            'academic_area',
            'branch_name',
            'has_lab',
            'prerequisite_ids',
        ]

    def get_prerequisite_ids(self, obj):
        return [p.required_course.public_id for p in obj.prerequisites.all()]


class ManagementCurriculumPlanSerializer(serializers.ModelSerializer):
    school_id = serializers.SlugRelatedField(
        source='school',
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.all(),
        write_only=True,
    )
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = CurriculumPlan
        fields = ['public_id', 'school_id', 'school_name', 'name', 'year', 'is_active']


class ManagementCourseSerializer(serializers.ModelSerializer):
    plan_id = serializers.SlugRelatedField(
        source='curriculum_plan',
        slug_field='public_id',
        queryset=CurriculumPlan.objects.all(),
        write_only=True,
    )
    branch_id = serializers.SlugRelatedField(
        source='branch',
        slug_field='public_id',
        queryset=ElectiveBranch.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Course
        fields = [
            'public_id',
            'plan_id',
            'branch_id',
            'code',
            'name',
            'credits',
            'theory_hours',
            'seminar_hours',
            'theory_practice_hours',
            'practice_hours',
            'lab_hours',
            'cycle',
            'course_type',
            'academic_area',
            'min_credits_required',
            'is_active',
        ]


class ManagementPrerequisiteSerializer(serializers.ModelSerializer):
    course_id = serializers.SlugRelatedField(
        source='course', slug_field='public_id', queryset=Course.objects.all(), write_only=True
    )
    required_course_id = serializers.SlugRelatedField(
        source='required_course',
        slug_field='public_id',
        queryset=Course.objects.all(),
        write_only=True,
    )

    course_name = serializers.CharField(source='course.name', read_only=True)
    required_course_name = serializers.CharField(source='required_course.name', read_only=True)

    class Meta:
        model = Prerequisite
        fields = [
            'public_id',
            'course_id',
            'required_course_id',
            'course_name',
            'required_course_name',
        ]