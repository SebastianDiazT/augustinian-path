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

from apps.accounts.permissions import IsPlatformAdmin
from apps.core.openapi import success_response_schema
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response
from apps.core.serializers import ApiErrorResponseSerializer

from .filters import (
    CourseFilter,
    CurriculumCourseFilter,
    CurriculumPlanFilter,
    FacultyFilter,
    ProfessionalSchoolFilter,
)
from .models import (
    Course,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from .serializers import (
    CourseListDataSerializer,
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
        responses=success_response_schema(
            component_name='PlatformAdminProfessionalSchoolSuccessResponse',
            data_serializer=ProfessionalSchoolSerializer,
        ),
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
        responses=success_response_schema(
            component_name='PlatformAdminProfessionalSchoolListSuccessResponse',
            data_serializer=ProfessionalSchoolListDataSerializer,
        ),
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


class PlatformAdminCurriculumPlanListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

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
        responses=success_response_schema(
            component_name='PlatformAdminCurriculumPlanListSuccessResponse',
            data_serializer=CurriculumPlanListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        plan_filter = CurriculumPlanFilter(
            data=request.query_params,
            queryset=(
                CurriculumPlan.objects.select_related(
                    'professional_school',
                    'professional_school__faculty',
                ).all()
            ),
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
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CurriculumPlanWriteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        plan = serializer.save()

        return success_response(
            data=CurriculumPlanSerializer(plan).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCurriculumPlanDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar un plan de estudios',
        tags=['Administración académica'],
        request=CurriculumPlanWriteSerializer,
        responses=success_response_schema(
            component_name='PlatformAdminCurriculumPlanSuccessResponse',
            data_serializer=CurriculumPlanSerializer,
        ),
    )
    def patch(
        self,
        request: Request,
        plan_id: UUID,
    ) -> Response:
        plan = get_object_or_404(
            CurriculumPlan.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ),
            public_id=plan_id,
        )

        serializer = CurriculumPlanWriteSerializer(
            plan,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_plan = serializer.save()

        return success_response(
            data=CurriculumPlanSerializer(
                updated_plan,
            ).data,
            request_id=request.request_id,
        )


class PlatformAdminCourseListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

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
        responses=success_response_schema(
            component_name='PlatformAdminCourseListSuccessResponse',
            data_serializer=CourseListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        course_filter = CourseFilter(
            data=request.query_params,
            queryset=(
                Course.objects.select_related(
                    'professional_school',
                    'professional_school__faculty',
                ).all()
            ),
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
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CourseWriteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        course = serializer.save()

        return success_response(
            data=CourseSerializer(course).data,
            request_id=request.request_id,
            status_code=status.HTTP_201_CREATED,
        )


class PlatformAdminCourseDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar una asignatura',
        tags=['Administración académica'],
        request=CourseWriteSerializer,
        responses=success_response_schema(
            component_name='PlatformAdminCourseSuccessResponse',
            data_serializer=CourseSerializer,
        ),
    )
    def patch(
        self,
        request: Request,
        course_id: UUID,
    ) -> Response:
        course = get_object_or_404(
            Course.objects.select_related(
                'professional_school',
                'professional_school__faculty',
            ),
            public_id=course_id,
        )

        serializer = CourseWriteSerializer(
            course,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_course = serializer.save()

        return success_response(
            data=CourseSerializer(updated_course).data,
            request_id=request.request_id,
        )


class PlatformAdminCurriculumCourseListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

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
        responses=success_response_schema(
            component_name='PlatformAdminCurriculumCourseListSuccessResponse',
            data_serializer=CurriculumCourseListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        curriculum_course_filter = CurriculumCourseFilter(
            data=request.query_params,
            queryset=(
                CurriculumCourse.objects.select_related(
                    'curriculum_plan',
                    'curriculum_plan__professional_school',
                    ('curriculum_plan__professional_school__faculty'),
                    'course',
                ).all()
            ),
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
        },
    )
    def post(self, request: Request) -> Response:
        serializer = CurriculumCourseWriteSerializer(
            data=request.data,
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
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    @extend_schema(
        summary='Actualizar una asignatura de un plan',
        tags=['Administración académica'],
        request=CurriculumCourseWriteSerializer,
        responses=success_response_schema(
            component_name='PlatformAdminCurriculumCourseSuccessResponse',
            data_serializer=CurriculumCourseSerializer,
        ),
    )
    def patch(
        self,
        request: Request,
        curriculum_course_id: UUID,
    ) -> Response:
        curriculum_course = get_object_or_404(
            CurriculumCourse.objects.select_related(
                'curriculum_plan',
                'curriculum_plan__professional_school',
                'curriculum_plan__professional_school__faculty',
                'course',
            ),
            public_id=curriculum_course_id,
        )

        serializer = CurriculumCourseWriteSerializer(
            curriculum_course,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_curriculum_course = serializer.save()

        return success_response(
            data=CurriculumCourseSerializer(
                updated_curriculum_course,
            ).data,
            request_id=request.request_id,
        )
