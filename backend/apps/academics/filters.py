from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    UUIDFilter,
)

from .models import Faculty, ProfessionalSchool


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
