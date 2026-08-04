from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import (
    Course,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)


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


class FacultyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            'name',
            'is_active',
        ]
        extra_kwargs = {
            'is_active': {
                'required': False,
            },
        }

    def validate_name(self, value: str) -> str:
        normalized_name = ' '.join(value.split())

        if not normalized_name:
            raise serializers.ValidationError(
                'El nombre de la facultad es obligatorio.'
            )

        existing_faculties = Faculty.objects.filter(
            name__iexact=normalized_name,
        )

        if self.instance is not None:
            existing_faculties = existing_faculties.exclude(
                pk=self.instance.pk,
            )

        if existing_faculties.exists():
            raise serializers.ValidationError('Ya existe una facultad con este nombre.')

        return normalized_name

    def validate(
        self,
        attrs: dict[str, object],
    ) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        return attrs

    def create(
        self,
        validated_data: dict[str, object],
    ) -> Faculty:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'name': ('Ya existe una facultad con este nombre.'),
                }
            ) from error

    def update(
        self,
        instance: Faculty,
        validated_data: dict[str, object],
    ) -> Faculty:
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'name': ('Ya existe una facultad con este nombre.'),
                }
            ) from error


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


class CurriculumPlanSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    professional_school = ProfessionalSchoolSerializer(
        read_only=True,
    )

    class Meta:
        model = CurriculumPlan
        fields = [
            'id',
            'professional_school',
            'code',
            'name',
            'is_active',
        ]
        read_only_fields = fields


class CurriculumPlanListDataSerializer(
    serializers.Serializer,
):
    curriculum_plans = CurriculumPlanSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    professional_school = ProfessionalSchoolSerializer(
        read_only=True,
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'professional_school',
            'code',
            'name',
            'is_active',
        ]
        read_only_fields = fields


class CourseListDataSerializer(serializers.Serializer):
    courses = CourseSerializer(many=True)
    pagination = AcademicPaginationSerializer()


class CourseReferenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'code',
            'name',
        ]
        read_only_fields = fields


class CurriculumCourseSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    curriculum_plan = CurriculumPlanSerializer(
        read_only=True,
    )
    course = CourseReferenceSerializer(
        read_only=True,
    )

    class Meta:
        model = CurriculumCourse
        fields = [
            'id',
            'curriculum_plan',
            'course',
            'cycle',
            'credits',
        ]
        read_only_fields = fields


class CurriculumCourseListDataSerializer(
    serializers.Serializer,
):
    curriculum_courses = CurriculumCourseSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()
