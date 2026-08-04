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
    CourseCatalogListDataSerializer,
    CourseCatalogSerializer,
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
        responses=FacultyCatalogListDataSerializer,
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
        responses=ProfessionalSchoolCatalogListDataSerializer,
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
        responses=CurriculumPlanCatalogListDataSerializer,
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
        responses=CourseCatalogListDataSerializer,
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
