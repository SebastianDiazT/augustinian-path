from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import SchoolDelegation, SchoolMembership

from .models import Course, CurriculumPlan
from .serializers import CourseMeshSerializer, CurriculumPlanCatalogSerializer


class PlanCatalogListView(generics.ListAPIView):
    """
    GET: (El Folleto Público) Lista los planes de estudio de una escuela.
    Debe ser público para que los alumnos nuevos puedan llenar el formulario de ingreso.
    """

    serializer_class = CurriculumPlanCatalogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = CurriculumPlan.objects.filter(is_active=True).order_by('-year')
        school_id = self.request.query_params.get('school')
        if school_id:
            qs = qs.filter(school__public_id=school_id)
        return qs


class CourseMeshListView(generics.ListAPIView):
    """
    GET: (La Bóveda Privada) Devuelve el GRAFO COMPLETO de cursos para un plan.
    ESTRICTAMENTE AISLADO: Solo para alumnos aprobados de esa escuela o sus delegados.
    """

    serializer_class = CourseMeshSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        qs = (
            Course.objects.filter(is_active=True)
            .select_related('branch')
            .prefetch_related('prerequisites__required_course')
            .order_by('cycle', 'name')
        )

        if not user.is_platform_admin:
            enrolled_schools = SchoolMembership.objects.filter(user=user).values_list(
                'school', flat=True
            )

            delegated_schools = SchoolDelegation.objects.filter(delegate=user).values_list(
                'school', flat=True
            )

            qs = qs.filter(
                Q(curriculum_plan__school__in=enrolled_schools)
                | Q(curriculum_plan__school__in=delegated_schools)
            )

        plan_id = self.request.query_params.get('plan')
        if plan_id:
            qs = qs.filter(curriculum_plan__public_id=plan_id)

        return qs
