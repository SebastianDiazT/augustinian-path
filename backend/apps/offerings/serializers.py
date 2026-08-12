from rest_framework import serializers

from apps.curricula.models import AcademicTerm, Course, Instructor

from .models import Meeting, Offering, Section, TimeBlock


class OfferingSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='public_id', queryset=Course.objects.all())
    academic_term = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=AcademicTerm.objects.filter(is_active=True),
    )

    class Meta:
        model = Offering
        fields = ['public_id', 'course', 'academic_term', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = ['public_id', 'order', 'start_time', 'end_time']
        read_only_fields = fields


class MeetingSerializer(serializers.ModelSerializer):
    time_block = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=TimeBlock.objects.filter(is_active=True),
    )

    class Meta:
        model = Meeting
        fields = ['public_id', 'day_of_week', 'time_block', 'room']
        read_only_fields = ['public_id']


class SectionSerializer(serializers.ModelSerializer):
    offering = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Offering.objects.filter(is_active=True),
    )
    instructor = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Instructor.objects.filter(is_active=True),
    )
    meetings = MeetingSerializer(many=True, read_only=True)
    expected_meeting_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Section
        fields = [
            'public_id',
            'offering',
            'section_type',
            'number',
            'instructor',
            'meetings',
            'expected_meeting_count',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['public_id', 'meetings', 'expected_meeting_count', 'created_at']


def validate_meeting_count_matches_course_hours(section, meetings_data):
    expected = section.expected_meeting_count
    actual = len(meetings_data)
    if actual != expected:
        raise serializers.ValidationError(
            f'Este grupo necesita {expected} bloques semanales según el plan '
            f'curricular, pero se enviaron {actual}.',
        )
