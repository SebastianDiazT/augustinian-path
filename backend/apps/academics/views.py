from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.openapi import success_response_schema
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response

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
    CourseCatalogListDataSerializer,
    CourseCatalogSerializer,
    CurriculumCourseCatalogListDataSerializer,
    CurriculumCourseCatalogSerializer,
    CurriculumPlanCatalogListDataSerializer,
    CurriculumPlanCatalogSerializer,
    FacultyCatalogListDataSerializer,
    FacultyReferenceSerializer,
    ProfessionalSchoolCatalogListDataSerializer,
    ProfessionalSchoolCatalogSerializer,
)


class FacultyCatalogListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary='Listar facultades activas de la UNSA',
        tags=['Catálogo académico'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Busca parcialmente por nombre.',
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
        responses=success_response_schema(
            component_name='FacultyCatalogListSuccessResponse',
            data_serializer=FacultyCatalogListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        faculty_filter = FacultyFilter(
            data=request.query_params,
            queryset=Faculty.objects.filter(
                is_active=True,
            ),
        )

        if not faculty_filter.is_valid():
            raise ValidationError(faculty_filter.errors)

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(
            faculty_filter.qs,
            request,
            view=self,
        )

        serializer = FacultyReferenceSerializer(
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


class ProfessionalSchoolCatalogListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary='Listar escuelas profesionales activas',
        tags=['Catálogo académico'],
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
            component_name='ProfessionalSchoolCatalogListSuccessResponse',
            data_serializer=ProfessionalSchoolCatalogListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        school_filter = ProfessionalSchoolFilter(
            data=request.query_params,
            queryset=(
                ProfessionalSchool.objects.select_related(
                    'faculty',
                ).filter(
                    is_active=True,
                    faculty__is_active=True,
                )
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

        serializer = ProfessionalSchoolCatalogSerializer(
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


class CurriculumPlanCatalogListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary='Listar planes de estudios activos',
        tags=['Catálogo académico'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Busca parcialmente por código o nombre.'),
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la escuela profesional.'),
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
            component_name='CurriculumPlanCatalogListSuccessResponse',
            data_serializer=CurriculumPlanCatalogListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        plan_filter = CurriculumPlanFilter(
            data=request.query_params,
            queryset=(
                CurriculumPlan.objects.select_related(
                    'professional_school',
                    'professional_school__faculty',
                ).filter(
                    is_active=True,
                    professional_school__is_active=True,
                    professional_school__faculty__is_active=True,
                )
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

        serializer = CurriculumPlanCatalogSerializer(
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


class CourseCatalogListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary='Listar asignaturas activas',
        tags=['Catálogo académico'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Busca parcialmente por código o nombre.'),
            ),
            OpenApiParameter(
                name='professional_school',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público de la escuela profesional.'),
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
            component_name='CourseCatalogListSuccessResponse',
            data_serializer=CourseCatalogListDataSerializer,
        ),
    )
    def get(self, request: Request) -> Response:
        course_filter = CourseFilter(
            data=request.query_params,
            queryset=(
                Course.objects.select_related(
                    'professional_school',
                    'professional_school__faculty',
                ).filter(
                    is_active=True,
                    professional_school__is_active=True,
                    professional_school__faculty__is_active=True,
                )
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

        serializer = CourseCatalogSerializer(
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


class CurriculumCourseCatalogListView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary='Listar asignaturas de planes activos',
        tags=['Catálogo académico'],
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Busca por código o nombre de la asignatura.'),
            ),
            OpenApiParameter(
                name='curriculum_plan',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description=('Filtra por el UUID público del plan.'),
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
            component_name='CurriculumCourseCatalogListSuccessResponse',
            data_serializer=CurriculumCourseCatalogListDataSerializer,
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
                ).filter(
                    curriculum_plan__is_active=True,
                    curriculum_plan__professional_school__is_active=True,
                    curriculum_plan__professional_school__faculty__is_active=True,
                    course__is_active=True,
                    course__professional_school__is_active=True,
                    course__professional_school__faculty__is_active=True,
                )
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

        serializer = CurriculumCourseCatalogSerializer(
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
