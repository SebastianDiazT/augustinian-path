from rest_framework import serializers

from .models import Faculty, ProfessionalSchool


class FacultySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )

    class Meta:
        model = Faculty
        fields = [
            'id',
            'name',
            'is_active',
        ]
        read_only_fields = fields


class AcademicPaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class FacultyListDataSerializer(serializers.Serializer):
    faculties = FacultySerializer(many=True)
    pagination = AcademicPaginationSerializer()


class FacultyReferenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )

    class Meta:
        model = Faculty
        fields = [
            'id',
            'name',
        ]
        read_only_fields = fields


class ProfessionalSchoolSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    faculty = FacultyReferenceSerializer(
        read_only=True,
    )

    class Meta:
        model = ProfessionalSchool
        fields = [
            'id',
            'faculty',
            'name',
            'is_active',
        ]
        read_only_fields = fields


class ProfessionalSchoolListDataSerializer(
    serializers.Serializer,
):
    professional_schools = ProfessionalSchoolSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()
