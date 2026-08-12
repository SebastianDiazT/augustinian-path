from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Area, Faculty, ProfessionalSchool


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['public_id', 'name', 'code', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'is_active', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Area.objects.all(),
                fields=['name'],
                message='Ya existe un área con este nombre.',
            )
        ]


class FacultySerializer(serializers.ModelSerializer):
    area = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Area.objects.filter(is_active=True),
    )

    class Meta:
        model = Faculty
        fields = ['public_id', 'area', 'name', 'code', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'is_active', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Faculty.objects.all(),
                fields=['area', 'name'],
                message='Ya existe una facultad con este nombre en esta área.',
            )
        ]


class ProfessionalSchoolSerializer(serializers.ModelSerializer):
    faculty = serializers.SlugRelatedField(
        slug_field='public_id',
        queryset=Faculty.objects.filter(is_active=True),
    )

    class Meta:
        model = ProfessionalSchool
        fields = ['public_id', 'faculty', 'name', 'code', 'is_active', 'created_at']
        read_only_fields = ['public_id', 'is_active', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=ProfessionalSchool.objects.all(),
                fields=['faculty', 'name'],
                message=(
                    'Ya existe una escuela profesional con este nombre dentro de esta facultad.'
                ),
            )
        ]
