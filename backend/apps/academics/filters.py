from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
)

from .models import Faculty


class FacultyFilter(FilterSet):
    search = CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )
    is_active = BooleanFilter()

    class Meta:
        model = Faculty
        fields: list[str] = []
