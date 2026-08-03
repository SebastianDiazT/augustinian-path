from django.db.models import Q, QuerySet
from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    FilterSet,
)

from .models import User
from .roles import Role


class PlatformAdminUserFilter(FilterSet):
    search = CharFilter(method='filter_search')
    role = ChoiceFilter(
        method='filter_role',
        choices=[(role.value, role.value) for role in Role],
    )
    is_active = BooleanFilter()

    class Meta:
        model = User
        fields: list[str] = []

    def filter_search(
        self,
        queryset: QuerySet[User],
        name: str,
        value: str,
    ) -> QuerySet[User]:
        search_term = value.strip()

        if not search_term:
            return queryset

        return queryset.filter(
            Q(email__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
        )

    def filter_role(
        self,
        queryset: QuerySet[User],
        name: str,
        value: str,
    ) -> QuerySet[User]:
        return queryset.filter(
            groups__name=value,
        ).distinct()
