from django.db.models import Q, QuerySet
from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
    UUIDFilter,
)

from .models import (
    Course,
    CurriculumCourse,
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


class CourseFilter(FilterSet):
    search = CharFilter(
        method='filter_search',
    )
    professional_school = UUIDFilter(
        field_name='professional_school__public_id',
    )
    is_active = BooleanFilter()

    class Meta:
        model = Course
        fields: list[str] = []

    def filter_search(
        self,
        queryset: QuerySet[Course],
        name: str,
        value: str,
    ) -> QuerySet[Course]:
        search_term = value.strip()

        if not search_term:
            return queryset

        return queryset.filter(
            Q(code__icontains=search_term) | Q(name__icontains=search_term)
        )


class CurriculumCourseFilter(FilterSet):
    search = CharFilter(
        method='filter_search',
    )
    curriculum_plan = UUIDFilter(
        field_name='curriculum_plan__public_id',
    )
    professional_school = UUIDFilter(
        field_name=('curriculum_plan__professional_school__public_id'),
    )
    cycle = NumberFilter()

    class Meta:
        model = CurriculumCourse
        fields: list[str] = []

    def filter_search(
        self,
        queryset: QuerySet[CurriculumCourse],
        name: str,
        value: str,
    ) -> QuerySet[CurriculumCourse]:
        search_term = value.strip()

        if not search_term:
            return queryset

        return queryset.filter(
            Q(course__code__icontains=search_term)
            | Q(course__name__icontains=search_term)
        )
