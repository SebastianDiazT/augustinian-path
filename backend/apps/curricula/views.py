from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsPlatformAdmin, IsSchoolDelegate

from .models import (
    AcademicTerm,
    Course,
    CurriculumPlan,
    ElectiveBranch,
    EvaluationComponent,
    Instructor,
    Prerequisite,
    Syllabus,
)
from .serializers import (
    AcademicTermSerializer,
    CourseSerializer,
    CurriculumPlanSerializer,
    ElectiveBranchSerializer,
    EvaluationComponentSerializer,
    InstructorSerializer,
    PrerequisiteSerializer,
    SyllabusSerializer,
    validate_component_weights_sum_to_100,
)


class _IsAdminOrDelegateOfRelatedSchool(IsSchoolDelegate):
    def has_object_permission(self, request, view, obj):
        if request.user.is_platform_admin:
            return True
        return super().has_object_permission(request, view, obj)


class _CatalogWritePermissionMixin:
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), _IsAdminOrDelegateOfRelatedSchool()]

    def perform_create(self, serializer):
        obj = serializer.save()
        if not self.request.user.is_platform_admin:
            school = obj.get_school()
            if not self.request.user.is_delegate_of(school):
                obj.delete()

                raise PermissionDenied('No tienes permiso para crear recursos en esta escuela.')


class CurriculumPlanViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = (
        CurriculumPlan.objects.filter(is_active=True)
        .select_related('school')
        .order_by('-created_at')
    )
    serializer_class = CurriculumPlanSerializer
    lookup_field = 'public_id'


class CourseViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True).select_related('curriculum_plan', 'branch')
    serializer_class = CourseSerializer
    lookup_field = 'public_id'
    filterset_fields = ['curriculum_plan', 'cycle', 'course_type']


class ElectiveBranchViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = ElectiveBranch.objects.filter(is_active=True).select_related('curriculum_plan')
    serializer_class = ElectiveBranchSerializer
    lookup_field = 'public_id'
    filterset_fields = ['curriculum_plan']


class PrerequisiteViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = Prerequisite.objects.select_related('course', 'required_course')
    serializer_class = PrerequisiteSerializer
    lookup_field = 'public_id'


class AcademicTermViewSet(viewsets.ModelViewSet):
    queryset = AcademicTerm.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AcademicTermSerializer
    lookup_field = 'public_id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsPlatformAdmin()]


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = InstructorSerializer
    lookup_field = 'public_id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsPlatformAdmin()]


class SyllabusViewSet(_CatalogWritePermissionMixin, viewsets.ModelViewSet):
    queryset = (
        Syllabus.objects.filter(is_active=True)
        .select_related(
            'course',
            'academic_term',
        )
        .prefetch_related('instructors', 'evaluation_components')
    )
    serializer_class = SyllabusSerializer
    lookup_field = 'public_id'
    filterset_fields = ['course', 'academic_term']

    @action(detail=True, methods=['put'], url_path='evaluation-components')
    def set_evaluation_components(self, request, public_id=None):
        syllabus = self.get_object()

        serializer = EvaluationComponentSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        validate_component_weights_sum_to_100(serializer.validated_data)

        with transaction.atomic():
            syllabus.evaluation_components.all().delete()
            components = [
                EvaluationComponent(syllabus=syllabus, **item) for item in serializer.validated_data
            ]
            EvaluationComponent.objects.bulk_create(components)

        syllabus.refresh_from_db()
        return Response(SyllabusSerializer(syllabus).data)
