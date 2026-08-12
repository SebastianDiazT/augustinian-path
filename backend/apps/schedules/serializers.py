from rest_framework import serializers

from apps.curricula.models import AcademicTerm
from apps.offerings.models import Offering, Section

from .models import PublicShareLink, ScheduleAlternative, ScheduleSimulation


class SectionSummarySerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='offering.course.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    meetings = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'public_id', 'course_name', 'section_type', 'number',
            'instructor_name', 'meetings',
        ]
        read_only_fields = fields

    def get_meetings(self, obj):
        return [
            {
                'day_of_week': meeting.day_of_week,
                'start_time': meeting.time_block.start_time,
                'end_time': meeting.time_block.end_time,
                'room': meeting.room,
            }
            for meeting in obj.meetings.all()
        ]


class ScheduleAlternativeSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleAlternative
        fields = ['public_id', 'score', 'description', 'rank', 'is_favorite', 'sections']
        read_only_fields = ['public_id', 'score', 'description', 'rank', 'sections']

    def get_sections(self, obj):
        bridge_rows = obj.sections.select_related(
            'section__offering__course', 'section__instructor',
        ).prefetch_related('section__meetings__time_block')
        sections = [row.section for row in bridge_rows]
        return SectionSummarySerializer(sections, many=True).data


class ScheduleSimulationSerializer(serializers.ModelSerializer):
    academic_term = serializers.SlugRelatedField(slug_field='public_id', read_only=True)
    offerings = serializers.SlugRelatedField(slug_field='public_id', many=True, read_only=True)
    alternatives = ScheduleAlternativeSerializer(many=True, read_only=True)

    class Meta:
        model = ScheduleSimulation
        fields = [
            'public_id', 'academic_term', 'offerings', 'preferences', 'notes',
            'alternatives', 'created_at',
        ]
        read_only_fields = fields


class GenerateSimulationSerializer(serializers.Serializer):
    """Input for the `generate` action — not a ModelSerializer, since the
    request shape (offering public_ids, exclusion lists) doesn't map 1:1
    onto ScheduleSimulation's own fields."""

    academic_term = serializers.SlugRelatedField(
        slug_field='public_id', queryset=AcademicTerm.objects.filter(is_active=True),
    )
    offerings = serializers.SlugRelatedField(
        slug_field='public_id', queryset=Offering.objects.filter(is_active=True), many=True,
    )
    excluded_sections = serializers.ListField(
        child=serializers.CharField(), required=False, default=list,
    )
    excluded_instructors = serializers.ListField(
        child=serializers.CharField(), required=False, default=list,
    )
    preferences = serializers.JSONField(required=False, default=dict)

    def validate_offerings(self, value):
        if not (1 <= len(value) <= 10):
            raise serializers.ValidationError('Selecciona entre 1 y 10 asignaturas.')
        return value


class PublicShareLinkSerializer(serializers.ModelSerializer):
    alternative = serializers.SlugRelatedField(
        slug_field='public_id', queryset=ScheduleAlternative.objects.all(),
    )

    class Meta:
        model = PublicShareLink
        fields = ['public_id', 'alternative', 'include_personal_info', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'is_active', 'created_at']


class PublicScheduleViewSerializer(serializers.ModelSerializer):
    """What an unauthenticated visitor sees at the public share link —
    read-only, no relation to the owning student unless they opted in."""

    alternative = ScheduleAlternativeSerializer(read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = PublicShareLink
        fields = ['public_id', 'alternative', 'student_name', 'created_at']
        read_only_fields = fields

    def get_student_name(self, obj):
        if obj.include_personal_info:
            return obj.alternative.simulation.student.user.full_name
        return None
