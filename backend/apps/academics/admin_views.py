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

from apps.accounts.permissions import IsPlatformAdmin
from apps.core.pagination import StandardPageNumberPagination
from apps.core.responses import success_response

from .filters import (
    CourseFilter,
    CurriculumPlanFilter,
    FacultyFilter,
    ProfessionalSchoolFilter,
)
from .models import (
    Course,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from .serializers import (
    CourseListDataSerializer,
    CourseSerializer,
    CurriculumPlanListDataSerializer,
    CurriculumPlanSerializer,
    FacultyListDataSerializer,
    FacultySerializer,
    ProfessionalSchoolListDataSerializer,
    ProfessionalSchoolSerializer,
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
        responses=FacultyListDataSerializer,
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
        responses=ProfessionalSchoolListDataSerializer,
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
        responses=CurriculumPlanListDataSerializer,
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
        responses=CourseListDataSerializer,
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
