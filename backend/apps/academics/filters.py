from django.db.models import Q, QuerySet
from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    UUIDFilter,
)

from .models import (
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)


class FacultyFilter(FilterSet):
    search = CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )
    is_active = BooleanFilter()

    class Meta:
        model = Faculty
        fields: list[str] = []


class ProfessionalSchoolFilter(FilterSet):
    search = CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )
    faculty = UUIDFilter(
        field_name='faculty__public_id',
    )
    is_active = BooleanFilter()

    class Meta:
        model = ProfessionalSchool
        fields: list[str] = []


class CurriculumPlanFilter(FilterSet):
    search = CharFilter(
        method='filter_search',
    )
    professional_school = UUIDFilter(
        field_name='professional_school__public_id',
    )
    is_active = BooleanFilter()

    class Meta:
        model = CurriculumPlan
        fields: list[str] = []

    def filter_search(
        self,
        queryset: QuerySet[CurriculumPlan],
        name: str,
        value: str,
    ) -> QuerySet[CurriculumPlan]:
        search_term = value.strip()

        if not search_term:
            return queryset

        return queryset.filter(
            Q(code__icontains=search_term) | Q(name__icontains=search_term)
        )
