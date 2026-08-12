from decimal import Decimal

from django.core import exceptions as drf_django_exceptions
from drf_spectacular.utils import extend_schema
from rest_framework import serializers as drf_serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOwnerStudent
from apps.curricula.models import CurriculumPlan

from .models import CourseEnrollment
from .progress import compute_eligible_courses, compute_progress
from .serializers import (
    AcademicProgressSerializer,
    CourseEnrollmentSerializer,
    EligibleCourseEntrySerializer,
    GradeSerializer,
    GradeSimulationResultSerializer,
    SimulateGradesRequestSerializer,
)
from .services import build_grade_scenarios


class _IsOwnerOrPlatformAdmin(IsOwnerStudent):
    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return super().has_object_permission(request, view, obj)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = CourseEnrollmentSerializer
    lookup_field = 'public_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = CourseEnrollment.objects.select_related(
            'offering__course', 'theory_section', 'lab_section',
        ).prefetch_related('grades__evaluation_component')
        if user.is_platform_admin:
            return qs
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        return qs.none()

    def get_permissions(self):
        if self.action in (
            'retrieve', 'update', 'partial_update', 'destroy', 'grades', 'simulate',
        ):
            return [IsAuthenticated(), _IsOwnerOrPlatformAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'student_profile'):
            raise drf_serializers.ValidationError(
                'Necesitas registrar tu perfil de estudiante antes de matricular un curso.',
            )
        serializer.save()

    @action(detail=True, methods=['get', 'post'])
    def grades(self, request, public_id=None):
        enrollment = self.get_object()

        if request.method == 'GET':
            return Response(GradeSerializer(enrollment.grades.all(), many=True).data)

        serializer = GradeSerializer(data=request.data, context={'enrollment': enrollment})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(GradeSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=SimulateGradesRequestSerializer,
        responses=GradeSimulationResultSerializer,
    )
    @action(detail=True, methods=['post'])
    def simulate(self, request, public_id=None):
        enrollment = self.get_object()
        syllabus = enrollment.get_syllabus()
        if syllabus is None:
            raise drf_serializers.ValidationError(
                'No se encontró el sílabo de este curso para este periodo.',
            )

        components = list(syllabus.evaluation_components.all())
        existing_grades = {
            str(grade.evaluation_component.public_id): grade.score
            for grade in enrollment.grades.select_related('evaluation_component')
        }
        requested_raw = request.data.get('expected_grades', {}) if request.data else {}
        requested_grades = {
            component_id: Decimal(str(value)) for component_id, value in requested_raw.items()
        }

        result = build_grade_scenarios(components, existing_grades, requested_grades)
        return Response(result)


class AcademicProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        curriculum_plan = self._get_plan(request)
        if not hasattr(request.user, 'student_profile'):
            raise drf_serializers.ValidationError(
                'Necesitas registrar tu perfil de estudiante primero.'
            )

        progress = compute_progress(request.user.student_profile, curriculum_plan)
        return Response(AcademicProgressSerializer(progress).data)

    def _get_plan(self, request):
        public_id = request.query_params.get('curriculum_plan')
        if not public_id:
            raise drf_serializers.ValidationError('Falta el parámetro curriculum_plan.')
        try:
            return CurriculumPlan.objects.get(public_id=public_id, is_active=True)
        except (
            CurriculumPlan.DoesNotExist,
            ValueError,
            drf_django_exceptions.ValidationError
        ) as e:
            raise drf_serializers.ValidationError('El plan curricular indicado no existe.') from e


class EligibleCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        curriculum_plan = self._get_plan(request)
        if not hasattr(request.user, 'student_profile'):
            raise drf_serializers.ValidationError(
                'Necesitas registrar tu perfil de estudiante primero.'
            )

        entries = compute_eligible_courses(request.user.student_profile, curriculum_plan)
        return Response(EligibleCourseEntrySerializer(entries, many=True).data)

    def _get_plan(self, request):
        public_id = request.query_params.get('curriculum_plan')
        if not public_id:
            raise drf_serializers.ValidationError('Falta el parámetro curriculum_plan.')
        try:
            return CurriculumPlan.objects.get(public_id=public_id, is_active=True)
        except (
            CurriculumPlan.DoesNotExist,
            ValueError,
            drf_django_exceptions.ValidationError
        ) as e:
            raise drf_serializers.ValidationError('El plan curricular indicado no existe.') from e
