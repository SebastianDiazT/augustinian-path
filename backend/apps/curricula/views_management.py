from rest_framework import filters, generics
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import SchoolDelegation
from apps.core.permissions import IsAdminOrDelegate

from .models import Course, CurriculumPlan, Prerequisite
from .serializers import (
    ManagementCourseSerializer,
    ManagementCurriculumPlanSerializer,
    ManagementPrerequisiteSerializer,
)


class BaseManagementView:
    """Clase base para inyectar la lógica de aislamiento multi-tenant."""

    permission_classes = [IsAdminOrDelegate]
    filter_backends = [filters.SearchFilter]

    def get_delegated_schools(self):
        user = self.request.user
        if user.is_platform_admin:
            return None
        return SchoolDelegation.objects.filter(delegate=user).values_list('school', flat=True)


# --- 1. PLANES DE ESTUDIO ---


class ManagementPlanListCreateView(BaseManagementView, generics.ListCreateAPIView):
    serializer_class = ManagementCurriculumPlanSerializer
    search_fields = ['name', 'year']

    def get_queryset(self):
        qs = CurriculumPlan.objects.all().order_by('-year')
        schools = self.get_delegated_schools()
        if schools is not None:
            qs = qs.filter(school__in=schools)
        return qs

    def perform_create(self, serializer):
        school = serializer.validated_data['school']
        self.check_object_permissions(self.request, school)
        serializer.save()


class ManagementPlanDetailView(BaseManagementView, generics.RetrieveUpdateDestroyAPIView):
    queryset = CurriculumPlan.objects.all()
    serializer_class = ManagementCurriculumPlanSerializer
    lookup_field = 'public_id'

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


# --- 2. CURSOS ---


class ManagementCourseListCreateView(BaseManagementView, generics.ListCreateAPIView):
    serializer_class = ManagementCourseSerializer
    search_fields = ['code', 'name']

    def get_queryset(self):
        qs = Course.objects.all().order_by('cycle', 'name')
        schools = self.get_delegated_schools()
        if schools is not None:
            qs = qs.filter(curriculum_plan__school__in=schools)

        plan_id = self.request.query_params.get('plan_id')
        if plan_id:
            qs = qs.filter(curriculum_plan__public_id=plan_id)
        return qs

    def perform_create(self, serializer):
        plan = serializer.validated_data['curriculum_plan']
        self.check_object_permissions(self.request, plan.school)
        serializer.save()


class ManagementCourseDetailView(BaseManagementView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = ManagementCourseSerializer
    lookup_field = 'public_id'

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])


# --- 3. PRERREQUISITOS (Las Flechas del Grafo) ---


class ManagementPrerequisiteListCreateView(BaseManagementView, generics.ListCreateAPIView):
    serializer_class = ManagementPrerequisiteSerializer

    def get_queryset(self):
        qs = Prerequisite.objects.all()
        schools = self.get_delegated_schools()
        if schools is not None:
            qs = qs.filter(course__curriculum_plan__school__in=schools)

        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course__public_id=course_id)
        return qs

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        required_course = serializer.validated_data['required_course']

        self.check_object_permissions(self.request, course.curriculum_plan.school)

        if course.curriculum_plan != required_course.curriculum_plan:
            raise PermissionDenied('Ambos cursos deben pertenecer al mismo plan de estudios.')

        serializer.save()


class ManagementPrerequisiteDetailView(BaseManagementView, generics.RetrieveDestroyAPIView):
    queryset = Prerequisite.objects.all()
    serializer_class = ManagementPrerequisiteSerializer
    lookup_field = 'public_id'
