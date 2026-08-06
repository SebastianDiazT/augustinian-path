from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import (
    IsPlatformAdmin,
    IsPlatformOrAcademicAdmin,
)
from apps.core.openapi import success_response_schema
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response
from apps.core.serializers import ApiErrorResponseSerializer

from .admin_scope import SchoolScopedAdminAPIView
from .filters import (
    AcademicPeriodFilter,
    CourseFilter,
    CourseOfferingFilter,
    CurriculumCourseFilter,
    CurriculumPlanFilter,
    FacultyFilter,
    ProfessionalSchoolFilter,
)
from .models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
    StudentCourseAttempt,
)
from .serializers import (
    AcademicPeriodListDataSerializer,
    AcademicPeriodSerializer,
    AcademicPeriodWriteSerializer,
    CourseListDataSerializer,
    CourseOfferingListDataSerializer,
    CourseOfferingSerializer,
    CourseOfferingWriteSerializer,
    CourseSerializer,
    CourseWriteSerializer,
    CurriculumCourseListDataSerializer,
    CurriculumCourseSerializer,
    CurriculumCourseWriteSerializer,
    CurriculumPlanListDataSerializer,
    CurriculumPlanSerializer,
    CurriculumPlanWriteSerializer,
    FacultyListDataSerializer,
    FacultySerializer,
    FacultyWriteSerializer,
    ProfessionalSchoolListDataSerializer,
    ProfessionalSchoolSerializer,
    ProfessionalSchoolWriteSerializer,
    StudentCourseAttemptSerializer,
    StudentCourseAttemptWriteSerializer,
)


class PlatformAdminFacultyListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Listar facultades de la UNSA',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Busca parcialmente por nombre.',
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de facultades por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminFacultyListSuccessResponse',
                data_serializer=FacultyListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        faculty_filter = FacultyFilter(
            data=request.query_params,
            queryset=Faculty.objects.all(),
        )

        if not faculty_filter.is_valid():
            raise ValidationError(faculty_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            faculty_filter.qs,
            request,
            view=self,
        )

        serializer = FacultySerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'faculties': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear una facultad de la UNSA',
        tags=['Administración académica'],
        request=FacultyWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name='PlatformAdminFacultySuccessResponse',
                data_serializer=FacultySerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = FacultyWriteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        faculty = serializer.save()

        return success_response(
            data=FacultySerializer(faculty).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminProfessionalSchoolDetailView(
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar una escuela profesional',
        tags=['Administración académica'],
        request=ProfessionalSchoolWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminProfessionalSchoolSuccessResponse',
                data_serializer=ProfessionalSchoolSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def patch(
        self,
        request: Request,
        school_id: UUID,
    ) -> Response:
        school = get_object_or_404(
            ProfessionalSchool.objects.select_related(
                'faculty',
            ),
            public_id=school_id,
        )

        serializer = ProfessionalSchoolWriteSerializer(
            school,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_school = serializer.save()

        return success_response(
            data=ProfessionalSchoolSerializer(
                updated_school,
            ).data,
            request_id=request.request_id,
        )


class PlatformAdminFacultyDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar una facultad de la UNSA',
        tags=['Administración académica'],
        request=FacultyWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminFacultySuccessResponse',
                data_serializer=FacultySerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def patch(
        self,
        request: Request,
        faculty_id: UUID,
    ) -> Response:
        faculty = get_object_or_404(
            Faculty,
            public_id=faculty_id,
        )

        serializer = FacultyWriteSerializer(
            faculty,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_faculty = serializer.save()

        return success_response(
            data=FacultySerializer(
                updated_faculty,
            ).data,
            request_id=request.request_id,
        )


class PlatformAdminProfessionalSchoolListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Listar escuelas profesionales de la UNSA',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Busca parcialmente por nombre.',
            ),
            OpenApiParameter(
                name='faculty',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la facultad.'),
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de escuelas por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminProfessionalSchoolListSuccessResponse',
                data_serializer=ProfessionalSchoolListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        school_filter = ProfessionalSchoolFilter(
            data=request.query_params,
            queryset=(
                ProfessionalSchool.objects.select_related(
                    'faculty',
                ).all()
            ),
        )

        if not school_filter.is_valid():
            raise ValidationError(school_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            school_filter.qs,
            request,
            view=self,
        )

        serializer = ProfessionalSchoolSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'professional_schools': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear una escuela profesional',
        tags=['Administración académica'],
        request=ProfessionalSchoolWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name='PlatformAdminProfessionalSchoolSuccessResponse',
                data_serializer=ProfessionalSchoolSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ProfessionalSchoolWriteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        school = serializer.save()

        return success_response(
            data=ProfessionalSchoolSerializer(
                school,
            ).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCurriculumPlanListView(SchoolScopedAdminAPIView):
    professional_school_lookup = 'professional_school_id'

    @extend_schema(
        summary='Listar planes de estudios de la UNSA',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Busca parcialmente por código o nombre.',
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la escuela profesional.'),
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de planes por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCurriculumPlanListSuccessResponse',
                data_serializer=CurriculumPlanListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CurriculumPlan.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ).all(),
        )

        plan_filter = CurriculumPlanFilter(
            data=request.query_params,
            queryset=queryset,
        )

        if not plan_filter.is_valid():
            raise ValidationError(plan_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            plan_filter.qs,
            request,
            view=self,
        )

        serializer = CurriculumPlanSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'curriculum_plans': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear un plan de estudios',
        tags=['Administración académica'],
        request=CurriculumPlanWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name='PlatformAdminCurriculumPlanSuccessResponse',
                data_serializer=CurriculumPlanSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CurriculumPlanWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        plan = serializer.save()

        return success_response(
            data=CurriculumPlanSerializer(plan).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCurriculumPlanDetailView(SchoolScopedAdminAPIView):
    professional_school_lookup = 'professional_school_id'

    @extend_schema(
        summary='Actualizar un plan de estudios',
        tags=['Administración académica'],
        request=CurriculumPlanWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCurriculumPlanSuccessResponse',
                data_serializer=CurriculumPlanSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def patch(
        self,
        request: Request,
        plan_id: UUID,
    ) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CurriculumPlan.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ),
        )

        plan = get_object_or_404(
            queryset,
            public_id=plan_id,
        )

        serializer = CurriculumPlanWriteSerializer(
            plan,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        updated_plan = serializer.save()

        return success_response(
            data=CurriculumPlanSerializer(
                updated_plan,
            ).data,
            request_id=request.request_id,
        )


class PlatformAdminCourseListView(SchoolScopedAdminAPIView):
    professional_school_lookup = 'professional_school_id'

    @extend_schema(
        summary='Listar asignaturas de la UNSA',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Busca parcialmente por código o nombre.',
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la escuela profesional.'),
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de asignaturas por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCourseListSuccessResponse',
                data_serializer=CourseListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            Course.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ).all(),
        )

        course_filter = CourseFilter(
            data=request.query_params,
            queryset=queryset,
        )

        if not course_filter.is_valid():
            raise ValidationError(course_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            course_filter.qs,
            request,
            view=self,
        )

        serializer = CourseSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'courses': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear una asignatura',
        tags=['Administración académica'],
        request=CourseWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name='PlatformAdminCourseSuccessResponse',
                data_serializer=CourseSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        course = serializer.save()

        return success_response(
            data=CourseSerializer(course).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCourseDetailView(SchoolScopedAdminAPIView):
    professional_school_lookup = 'professional_school_id'

    @extend_schema(
        summary='Actualizar una asignatura',
        tags=['Administración académica'],
        request=CourseWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCourseSuccessResponse',
                data_serializer=CourseSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def patch(
        self,
        request: Request,
        course_id: UUID,
    ) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            Course.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ).all(),
        )

        course = get_object_or_404(
            queryset,
            public_id=course_id,
        )

        serializer = CourseWriteSerializer(
            course,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        updated_course = serializer.save()

        return success_response(
            data=CourseSerializer(updated_course).data,
            request_id=request.request_id,
        )


class PlatformAdminCurriculumCourseListView(
    SchoolScopedAdminAPIView,
):
    professional_school_lookup = 'curriculum_plan__professional_school_id'

    @extend_schema(
        summary='Listar asignaturas de planes de estudios',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    'Busca parcialmente por código o nombre de la asignatura.'
                ),
            ),
            OpenApiParameter(
                name='curriculum_plan',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público del plan.'),
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la escuela.'),
            ),
            OpenApiParameter(
                name='cycle',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por ciclo académico.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de registros por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCurriculumCourseListSuccessResponse',
                data_serializer=CurriculumCourseListDataSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CurriculumCourse.objects.select_related(
                'curriculum_plan',
                'curriculum_plan__professional_school',
                'curriculum_plan__professional_school__faculty',
                'course',
            )
            .prefetch_related(
                'prerequisites__course',
            )
            .all(),
        )

        curriculum_course_filter = CurriculumCourseFilter(
            data=request.query_params,
            queryset=queryset,
        )

        if not curriculum_course_filter.is_valid():
            raise ValidationError(curriculum_course_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            curriculum_course_filter.qs,
            request,
            view=self,
        )

        serializer = CurriculumCourseSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'curriculum_courses': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Agregar una asignatura a un plan de estudios',
        tags=['Administración académica'],
        request=CurriculumCourseWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name='PlatformAdminCurriculumCourseSuccessResponse',
                data_serializer=CurriculumCourseSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CurriculumCourseWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        curriculum_course = serializer.save()

        return success_response(
            data=CurriculumCourseSerializer(
                curriculum_course,
            ).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCurriculumCourseDetailView(
    SchoolScopedAdminAPIView,
):
    professional_school_lookup = 'curriculum_plan__professional_school_id'

    @extend_schema(
        summary='Actualizar una asignatura de un plan',
        tags=['Administración académica'],
        request=CurriculumCourseWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name='PlatformAdminCurriculumCourseSuccessResponse',
                data_serializer=CurriculumCourseSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: ApiErrorResponseSerializer,
            status.HTTP_403_FORBIDDEN: ApiErrorResponseSerializer,
            status.HTTP_404_NOT_FOUND: ApiErrorResponseSerializer,
        },
    )
    def patch(
        self,
        request: Request,
        curriculum_course_id: UUID,
    ) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CurriculumCourse.objects.select_related(
                'curriculum_plan',
                'curriculum_plan__professional_school',
                'curriculum_plan__professional_school__faculty',
                'course',
            )
            .prefetch_related(
                'prerequisites__course',
            )
            .all(),
        )

        curriculum_course = get_object_or_404(
            queryset,
            public_id=curriculum_course_id,
        )

        serializer = CurriculumCourseWriteSerializer(
            curriculum_course,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(raise_exception=True)

        updated_curriculum_course = serializer.save()

        return success_response(
            data=CurriculumCourseSerializer(
                updated_curriculum_course,
            ).data,
            request_id=request.request_id,
        )


class AcademicPeriodListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [
                IsAuthenticated,
                IsPlatformOrAcademicAdmin,
            ]
        else:
            permission_classes = self.permission_classes

        return [permission() for permission in permission_classes]

    @extend_schema(
        summary='Listar periodos académicos',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='year',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por año académico.',
            ),
            OpenApiParameter(
                name='term',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por semestre A o B.',
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de periodos por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('AcademicPeriodListSuccessResponse'),
                data_serializer=(AcademicPeriodListDataSerializer),
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
            status.HTTP_404_NOT_FOUND: (ApiErrorResponseSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        period_filter = AcademicPeriodFilter(
            data=request.query_params,
            queryset=AcademicPeriod.objects.all(),
        )

        if not period_filter.is_valid():
            raise ValidationError(
                period_filter.errors,
            )

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            period_filter.qs,
            request,
            view=self,
        )

        serializer = AcademicPeriodSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'academic_periods': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear un periodo académico',
        tags=['Administración académica'],
        request=AcademicPeriodWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name=('AcademicPeriodSuccessResponse'),
                data_serializer=AcademicPeriodSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = AcademicPeriodWriteSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        period = serializer.save()

        return success_response(
            data=AcademicPeriodSerializer(
                period,
            ).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class AcademicPeriodDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar un periodo académico',
        tags=['Administración académica'],
        request=AcademicPeriodWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('AcademicPeriodSuccessResponse'),
                data_serializer=AcademicPeriodSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
            status.HTTP_404_NOT_FOUND: (ApiErrorResponseSerializer),
        },
    )
    def patch(
        self,
        request: Request,
        period_id: UUID,
    ) -> Response:
        period = get_object_or_404(
            AcademicPeriod,
            public_id=period_id,
        )

        serializer = AcademicPeriodWriteSerializer(
            period,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        updated_period = serializer.save()

        return success_response(
            data=AcademicPeriodSerializer(
                updated_period,
            ).data,
            request_id=request.request_id,
        )


class CourseOfferingListView(
    SchoolScopedAdminAPIView,
):
    professional_school_lookup = 'course__professional_school_id'

    @extend_schema(
        summary='Listar ofertas de asignaturas',
        tags=['Administración académica'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Busca por código o nombre de asignatura.'),
            ),
            OpenApiParameter(
                name='academic_period',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por periodo académico.',
            ),
            OpenApiParameter(
                name='year',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por año.',
            ),
            OpenApiParameter(
                name='term',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por semestre A o B.',
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por escuela profesional.',
            ),
            OpenApiParameter(
                name='course',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por asignatura.',
            ),
            OpenApiParameter(
                name='is_active',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtra por estado activo.',
            ),
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Número de página.',
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Cantidad de ofertas por página. Máximo: 100.'),
            ),
        ],
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('CourseOfferingListSuccessResponse'),
                data_serializer=(CourseOfferingListDataSerializer),
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
            status.HTTP_404_NOT_FOUND: (ApiErrorResponseSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CourseOffering.objects.select_related(
                'academic_period',
                'course',
                'course__professional_school',
                'course__professional_school__faculty',
            )
            .prefetch_related(
                'curriculum_courses__course',
                'curriculum_courses__curriculum_plan__professional_school__faculty',
            )
            .all(),
        )

        offering_filter = CourseOfferingFilter(
            data=request.query_params,
            queryset=queryset,
        )

        if not offering_filter.is_valid():
            raise ValidationError(
                offering_filter.errors,
            )

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            offering_filter.qs,
            request,
            view=self,
        )

        serializer = CourseOfferingSerializer(
            page,
            many=True,
        )

        return success_response(
            data={
                'course_offerings': serializer.data,
                'pagination': paginator.get_metadata(),
            },
            request_id=request.request_id,
        )

    @extend_schema(
        summary='Crear una oferta de asignatura',
        tags=['Administración académica'],
        request=CourseOfferingWriteSerializer,
        responses={
            status.HTTP_201_CREATED: success_response_schema(
                component_name=('CourseOfferingSuccessResponse'),
                data_serializer=CourseOfferingSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseOfferingWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(
            raise_exception=True,
        )

        offering = serializer.save()

        return success_response(
            data=CourseOfferingSerializer(
                offering,
            ).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class CourseOfferingDetailView(
    SchoolScopedAdminAPIView,
):
    professional_school_lookup = 'course__professional_school_id'

    @extend_schema(
        summary='Actualizar una oferta de asignatura',
        tags=['Administración académica'],
        request=CourseOfferingWriteSerializer,
        responses={
            status.HTTP_200_OK: success_response_schema(
                component_name=('CourseOfferingSuccessResponse'),
                data_serializer=CourseOfferingSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: (ApiErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: (ApiErrorResponseSerializer),
            status.HTTP_404_NOT_FOUND: (ApiErrorResponseSerializer),
        },
    )
    def patch(
        self,
        request: Request,
        offering_id: UUID,
    ) -> Response:
        queryset = self.get_scoped_queryset(
            request,
            CourseOffering.objects.select_related(
                'academic_period',
                'course',
                'course__professional_school',
                'course__professional_school__faculty',
            )
            .prefetch_related(
                'curriculum_courses__course',
                'curriculum_courses__curriculum_plan__professional_school__faculty',
            )
            .all(),
        )

        offering = get_object_or_404(
            queryset,
            public_id=offering_id,
        )

        serializer = CourseOfferingWriteSerializer(
            offering,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(
                request,
            ),
        )
        serializer.is_valid(
            raise_exception=True,
        )

        updated_offering = serializer.save()

        return success_response(
            data=CourseOfferingSerializer(
                updated_offering,
            ).data,
            request_id=request.request_id,
        )


def student_course_attempt_queryset():
    return StudentCourseAttempt.objects.select_related(
        'student',
        'course_offering',
        'course_offering__academic_period',
        'course_offering__course',
        'curriculum_course',
        'curriculum_course__curriculum_plan',
    )


class StudentCourseAttemptListView(SchoolScopedAdminAPIView):
    serializer_class = StudentCourseAttemptSerializer
    professional_school_lookup = (
        'course_offering__course__professional_school_id'
    )

    def get(self, request: Request) -> Response:
        attempts = self.get_scoped_queryset(
            request,
            student_course_attempt_queryset(),
        )

        return success_response(
            data={
                'student_course_attempts': StudentCourseAttemptSerializer(
                    attempts,
                    many=True,
                ).data,
            },
            request_id=request.request_id,
        )

    def post(self, request: Request) -> Response:
        serializer = StudentCourseAttemptWriteSerializer(
            data=request.data,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()

        return success_response(
            data=StudentCourseAttemptSerializer(attempt).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class StudentCourseAttemptDetailView(SchoolScopedAdminAPIView):
    serializer_class = StudentCourseAttemptWriteSerializer
    professional_school_lookup = (
        'course_offering__course__professional_school_id'
    )

    def patch(
        self,
        request: Request,
        attempt_id: UUID,
    ) -> Response:
        attempt = get_object_or_404(
            self.get_scoped_queryset(
                request,
                student_course_attempt_queryset(),
            ),
            public_id=attempt_id,
        )
        serializer = StudentCourseAttemptWriteSerializer(
            attempt,
            data=request.data,
            partial=True,
            context=self.get_write_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        updated_attempt = serializer.save()

        return success_response(
            data=StudentCourseAttemptSerializer(updated_attempt).data,
            request_id=request.request_id,
        )
