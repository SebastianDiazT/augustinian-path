from rest_framework import serializers

from .models import Faculty, ProfessionalSchool


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['public_id', 'name', 'acronym', 'area', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'created_at']


class ProfessionalSchoolSerializer(serializers.ModelSerializer):
    faculty_id = serializers.SlugRelatedField(
        source='faculty', slug_field='public_id', queryset=Faculty.objects.all(), write_only=True
    )
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = ProfessionalSchool
        fields = [
            'public_id',
            'name',
            'acronym',
            'faculty_id',
            'faculty',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['public_id', 'created_at']
