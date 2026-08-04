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


class FacultyCatalogListDataSerializer(
    serializers.Serializer,
):
    faculties = FacultyReferenceSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()


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


class ProfessionalSchoolCatalogSerializer(
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
        ]
        read_only_fields = fields


class ProfessionalSchoolCatalogListDataSerializer(
    serializers.Serializer,
):
    professional_schools = ProfessionalSchoolCatalogSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()


class ProfessionalSchoolWriteSerializer(
    serializers.ModelSerializer,
):
    faculty_id = serializers.SlugRelatedField(
        source='faculty',
        slug_field='public_id',
        queryset=Faculty.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ProfessionalSchool
        fields = [
            'faculty_id',
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
            raise serializers.ValidationError('El nombre de la escuela es obligatorio.')

        return normalized_name

    def validate(
        self,
        attrs: dict[str, object],
    ) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        faculty = attrs.get('faculty')
        name = attrs.get('name')

        if self.instance is not None:
            if faculty is None:
                faculty = self.instance.faculty

            if name is None:
                name = self.instance.name

        if isinstance(faculty, Faculty) and isinstance(name, str):
            existing_schools = ProfessionalSchool.objects.filter(
                faculty=faculty,
                name__iexact=name,
            )

            if self.instance is not None:
                existing_schools = existing_schools.exclude(
                    pk=self.instance.pk,
                )

            if existing_schools.exists():
                raise serializers.ValidationError(
                    {
                        'name': (
                            'Ya existe una escuela profesional '
                            'con este nombre en la facultad '
                            'seleccionada.'
                        ),
                    }
                )

        return attrs

    def create(
        self,
        validated_data: dict[str, object],
    ) -> ProfessionalSchool:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'name': (
                        'Ya existe una escuela profesional '
                        'con este nombre en la facultad '
                        'seleccionada.'
                    ),
                }
            ) from error

    def update(
        self,
        instance: ProfessionalSchool,
        validated_data: dict[str, object],
    ) -> ProfessionalSchool:
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'name': (
                        'Ya existe una escuela profesional '
                        'con este nombre en la facultad '
                        'seleccionada.'
                    ),
                }
            ) from error


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


class CurriculumPlanCatalogSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    professional_school = ProfessionalSchoolCatalogSerializer(
        read_only=True,
    )

    class Meta:
        model = CurriculumPlan
        fields = [
            'id',
            'professional_school',
            'code',
            'name',
        ]
        read_only_fields = fields


class CurriculumPlanCatalogListDataSerializer(
    serializers.Serializer,
):
    curriculum_plans = CurriculumPlanCatalogSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()


class CurriculumPlanWriteSerializer(
    serializers.ModelSerializer,
):
    professional_school_id = serializers.SlugRelatedField(
        source='professional_school',
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.all(),
        write_only=True,
    )

    class Meta:
        model = CurriculumPlan
        fields = [
            'professional_school_id',
            'code',
            'name',
            'is_active',
        ]
        extra_kwargs = {
            'is_active': {
                'required': False,
            },
        }

    def validate_code(self, value: str) -> str:
        normalized_code = ' '.join(value.split()).upper()

        if not normalized_code:
            raise serializers.ValidationError('El código del plan es obligatorio.')

        return normalized_code

    def validate_name(self, value: str) -> str:
        normalized_name = ' '.join(value.split())

        if not normalized_name:
            raise serializers.ValidationError('El nombre del plan es obligatorio.')

        return normalized_name

    def validate(
        self,
        attrs: dict[str, object],
    ) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        school = attrs.get('professional_school')
        code = attrs.get('code')

        if self.instance is not None:
            current_school = self.instance.professional_school

            if (
                isinstance(school, ProfessionalSchool)
                and school.pk != current_school.pk
            ):
                raise serializers.ValidationError(
                    {
                        'professional_school_id': (
                            'No se puede cambiar la escuela '
                            'profesional de un plan existente.'
                        ),
                    }
                )

            school = current_school

            if code is None:
                code = self.instance.code

        if isinstance(school, ProfessionalSchool) and isinstance(code, str):
            existing_plans = CurriculumPlan.objects.filter(
                professional_school=school,
                code__iexact=code,
            )

            if self.instance is not None:
                existing_plans = existing_plans.exclude(
                    pk=self.instance.pk,
                )

            if existing_plans.exists():
                raise serializers.ValidationError(
                    {
                        'code': (
                            'Ya existe un plan con este código '
                            'en la escuela seleccionada.'
                        ),
                    }
                )

        return attrs

    def create(
        self,
        validated_data: dict[str, object],
    ) -> CurriculumPlan:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'code': (
                        'Ya existe un plan con este código en la escuela seleccionada.'
                    ),
                }
            ) from error

    def update(
        self,
        instance: CurriculumPlan,
        validated_data: dict[str, object],
    ) -> CurriculumPlan:
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'code': (
                        'Ya existe un plan con este código en la escuela seleccionada.'
                    ),
                }
            ) from error


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


class CourseCatalogSerializer(
    serializers.ModelSerializer,
):
    id = serializers.UUIDField(
        source='public_id',
        read_only=True,
    )
    professional_school = ProfessionalSchoolCatalogSerializer(
        read_only=True,
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'professional_school',
            'code',
            'name',
        ]
        read_only_fields = fields


class CourseCatalogListDataSerializer(
    serializers.Serializer,
):
    courses = CourseCatalogSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()


class CourseWriteSerializer(serializers.ModelSerializer):
    professional_school_id = serializers.SlugRelatedField(
        source='professional_school',
        slug_field='public_id',
        queryset=ProfessionalSchool.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Course
        fields = [
            'professional_school_id',
            'code',
            'name',
            'is_active',
        ]
        extra_kwargs = {
            'is_active': {
                'required': False,
            },
        }

    def validate_code(self, value: str) -> str:
        normalized_code = ' '.join(value.split()).upper()

        if not normalized_code:
            raise serializers.ValidationError(
                'El código de la asignatura es obligatorio.'
            )

        return normalized_code

    def validate_name(self, value: str) -> str:
        normalized_name = ' '.join(value.split())

        if not normalized_name:
            raise serializers.ValidationError(
                'El nombre de la asignatura es obligatorio.'
            )

        return normalized_name

    def validate(
        self,
        attrs: dict[str, object],
    ) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        school = attrs.get('professional_school')
        code = attrs.get('code')

        if self.instance is not None:
            current_school = self.instance.professional_school

            if (
                isinstance(school, ProfessionalSchool)
                and school.pk != current_school.pk
            ):
                raise serializers.ValidationError(
                    {
                        'professional_school_id': (
                            'No se puede cambiar la escuela '
                            'profesional de una asignatura '
                            'existente.'
                        ),
                    }
                )

            school = current_school

            if code is None:
                code = self.instance.code

        if isinstance(school, ProfessionalSchool) and isinstance(code, str):
            existing_courses = Course.objects.filter(
                professional_school=school,
                code__iexact=code,
            )

            if self.instance is not None:
                existing_courses = existing_courses.exclude(
                    pk=self.instance.pk,
                )

            if existing_courses.exists():
                raise serializers.ValidationError(
                    {
                        'code': (
                            'Ya existe una asignatura con este '
                            'código en la escuela seleccionada.'
                        ),
                    }
                )

        return attrs

    def create(
        self,
        validated_data: dict[str, object],
    ) -> Course:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'code': (
                        'Ya existe una asignatura con este '
                        'código en la escuela seleccionada.'
                    ),
                }
            ) from error

    def update(
        self,
        instance: Course,
        validated_data: dict[str, object],
    ) -> Course:
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'code': (
                        'Ya existe una asignatura con este '
                        'código en la escuela seleccionada.'
                    ),
                }
            ) from error


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


class CurriculumCourseWriteSerializer(
    serializers.ModelSerializer,
):
    curriculum_plan_id = serializers.SlugRelatedField(
        source='curriculum_plan',
        slug_field='public_id',
        queryset=CurriculumPlan.objects.all(),
        write_only=True,
    )
    course_id = serializers.SlugRelatedField(
        source='course',
        slug_field='public_id',
        queryset=Course.objects.all(),
        write_only=True,
    )

    class Meta:
        model = CurriculumCourse
        fields = [
            'curriculum_plan_id',
            'course_id',
            'cycle',
            'credits',
        ]
        validators = []

    def validate(
        self,
        attrs: dict[str, object],
    ) -> dict[str, object]:
        if self.partial and not attrs:
            raise serializers.ValidationError('Debes proporcionar al menos un campo.')

        curriculum_plan = attrs.get('curriculum_plan')
        course = attrs.get('course')

        if self.instance is not None:
            current_plan = self.instance.curriculum_plan
            current_course = self.instance.course

            immutable_errors = {}

            if (
                isinstance(curriculum_plan, CurriculumPlan)
                and curriculum_plan.pk != current_plan.pk
            ):
                immutable_errors['curriculum_plan_id'] = (
                    'No se puede cambiar el plan de estudios '
                    'de una asignatura ya vinculada.'
                )

            if isinstance(course, Course) and course.pk != current_course.pk:
                immutable_errors['course_id'] = (
                    'No se puede cambiar la asignatura de un registro existente.'
                )

            if immutable_errors:
                raise serializers.ValidationError(immutable_errors)

            curriculum_plan = current_plan
            course = current_course

        if isinstance(curriculum_plan, CurriculumPlan) and isinstance(course, Course):
            if curriculum_plan.professional_school_id != course.professional_school_id:
                raise serializers.ValidationError(
                    {
                        'course_id': (
                            'La asignatura y el plan de estudios '
                            'deben pertenecer a la misma escuela '
                            'profesional.'
                        ),
                    }
                )

            existing_entries = CurriculumCourse.objects.filter(
                curriculum_plan=curriculum_plan,
                course=course,
            )

            if self.instance is not None:
                existing_entries = existing_entries.exclude(
                    pk=self.instance.pk,
                )

            if existing_entries.exists():
                raise serializers.ValidationError(
                    {
                        'course_id': (
                            'La asignatura ya pertenece al plan '
                            'de estudios seleccionado.'
                        ),
                    }
                )

        return attrs

    def create(
        self,
        validated_data: dict[str, object],
    ) -> CurriculumCourse:
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'course_id': (
                        'La asignatura ya pertenece al plan de estudios seleccionado.'
                    ),
                }
            ) from error

    def update(
        self,
        instance: CurriculumCourse,
        validated_data: dict[str, object],
    ) -> CurriculumCourse:
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    'course_id': (
                        'La asignatura ya pertenece al plan de estudios seleccionado.'
                    ),
                }
            ) from error


class CurriculumCourseListDataSerializer(
    serializers.Serializer,
):
    curriculum_courses = CurriculumCourseSerializer(
        many=True,
    )
    pagination = AcademicPaginationSerializer()
