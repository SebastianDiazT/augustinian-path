from rest_framework import serializers

from apps.curricula.models import EvaluationComponent
from apps.curricula.serializers import CourseSerializer
from apps.offerings.models import Offering, Section

from .models import CourseEnrollment, Grade


class GradeSerializer(serializers.ModelSerializer):
    evaluation_component = serializers.SlugRelatedField(
        slug_field='public_id', queryset=EvaluationComponent.objects.all(),
    )

    class Meta:
        model = Grade
        fields = ['public_id', 'evaluation_component', 'score', 'created_at']
        read_only_fields = ['public_id', 'created_at']

    def validate(self, attrs):
        enrollment = self.context['enrollment']
        syllabus = enrollment.get_syllabus()
        component = attrs['evaluation_component']
        if syllabus is None or component.syllabus_id != syllabus.id:
            raise serializers.ValidationError(
                'Este componente de evaluación no pertenece al sílabo de este curso.',
            )
        return attrs

    def create(self, validated_data):
        validated_data['enrollment'] = self.context['enrollment']
        return super().create(validated_data)


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    offering = serializers.SlugRelatedField(
        slug_field='public_id', queryset=Offering.objects.filter(is_active=True),
    )
    theory_section = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Section.objects.filter(is_active=True, section_type=Section.SectionType.THEORY),
    )
    lab_section = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Section.objects.filter(is_active=True, section_type=Section.SectionType.LAB),
        required=False,
        allow_null=True,
    )
    grades = GradeSerializer(many=True, read_only=True)
    weighted_average = serializers.SerializerMethodField()

    class Meta:
        model = CourseEnrollment
        fields = [
            'public_id', 'offering', 'theory_section', 'lab_section', 'status',
            'grades', 'weighted_average', 'created_at',
        ]
        read_only_fields = ['public_id', 'status', 'grades', 'weighted_average', 'created_at']

    def get_weighted_average(self, obj):
        return str(obj.compute_weighted_average())

    def validate(self, attrs):
        offering = attrs.get('offering', getattr(self.instance, 'offering', None))
        theory_section = attrs.get('theory_section', getattr(self.instance, 'theory_section', None))
        lab_section = attrs.get('lab_section', getattr(self.instance, 'lab_section', None))

        if not offering or not theory_section:
            return attrs

        has_lab = offering.course.has_lab

        if 'offering' in attrs or 'lab_section' in attrs:
            if has_lab and lab_section is None:
                raise serializers.ValidationError(
                    'Este curso tiene laboratorio: debes indicar el grupo de laboratorio.',
                )
            if not has_lab and lab_section is not None:
                raise serializers.ValidationError(
                    'Este curso no tiene laboratorio: no debes indicar un grupo de laboratorio.',
                )

        if theory_section.offering_id != offering.id:
            raise serializers.ValidationError('El grupo de teoría no pertenece a esta oferta.')
        if lab_section and lab_section.offering_id != offering.id:
            raise serializers.ValidationError('El grupo de laboratorio no pertenece a esta oferta.')

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['student'] = request.user.student_profile
        return super().create(validated_data)


class AcademicProgressSerializer(serializers.Serializer):
    credits_completed = serializers.DecimalField(max_digits=6, decimal_places=1)
    credits_total_required = serializers.DecimalField(
        max_digits=6, decimal_places=1, allow_null=True,
    )
    progress_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=1, allow_null=True,
    )
    courses_passed = serializers.IntegerField()
    courses_total_in_plan = serializers.IntegerField()
    courses_in_progress = serializers.IntegerField()
    elective_branches_completed = serializers.IntegerField()
    elective_branches_required = serializers.IntegerField()


class EligibleCourseEntrySerializer(serializers.Serializer):
    course = CourseSerializer(read_only=True)
    is_eligible = serializers.BooleanField()
    is_in_progress = serializers.BooleanField()
    missing_prerequisites = CourseSerializer(many=True, read_only=True)
    missing_credits = serializers.DecimalField(
        max_digits=5, decimal_places=1, allow_null=True,
    )


class SimulateGradesRequestSerializer(serializers.Serializer):
    expected_grades = serializers.DictField(
        child=serializers.DecimalField(max_digits=4, decimal_places=2),
        required=False,
        help_text=(
            'Maps an evaluation_component public_id to an expected score, '
            'for the "custom" scenario.'
        ),
    )


class GradeScenarioSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    required_grades = serializers.DictField(child=serializers.CharField())
    projected_final_score = serializers.CharField()
    passes = serializers.BooleanField()
    feasible = serializers.BooleanField()


class GradeSimulationResultSerializer(serializers.Serializer):
    already_complete = serializers.BooleanField()
    final_score = serializers.CharField(required=False)
    passes = serializers.BooleanField(required=False)
    scenarios = GradeScenarioSerializer(many=True, required=False)
