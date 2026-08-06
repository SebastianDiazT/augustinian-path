from dataclasses import dataclass

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import AcademicAdminAssignment
from apps.accounts.permissions import IsPlatformOrAcademicAdmin
from apps.accounts.roles import Role


@dataclass(frozen=True)
class AcademicAdministrationScope:
    professional_school_id: int | None

    @property
    def is_global(self) -> bool:
        return self.professional_school_id is None


class SchoolScopedAdminAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformOrAcademicAdmin,
    ]
    professional_school_lookup = ''

    def get_administration_scope(
        self,
        request: Request,
    ) -> AcademicAdministrationScope:
        cached_scope = getattr(
            request,
            '_academic_administration_scope',
            None,
        )

        if isinstance(
            cached_scope,
            AcademicAdministrationScope,
        ):
            return cached_scope

        role_names = set(
            request.user.groups.filter(
                name__in=[
                    Role.PLATFORM_ADMIN.value,
                    Role.ACADEMIC_ADMIN.value,
                ]
            ).values_list(
                'name',
                flat=True,
            )
        )

        if Role.PLATFORM_ADMIN.value in role_names:
            scope = AcademicAdministrationScope(
                professional_school_id=None,
            )
        else:
            if Role.ACADEMIC_ADMIN.value not in role_names:
                raise PermissionDenied(
                    detail=('No tienes permisos de administración académica.'),
                    code='admin_required',
                )

            school_id = (
                AcademicAdminAssignment.objects.filter(
                    user=request.user,
                    professional_school__is_active=True,
                )
                .values_list(
                    'professional_school_id',
                    flat=True,
                )
                .first()
            )

            if school_id is None:
                raise PermissionDenied(
                    detail=('No tienes una escuela profesional activa asignada.'),
                    code='academic_admin_assignment_required',
                )

            scope = AcademicAdministrationScope(
                professional_school_id=school_id,
            )

        request._academic_administration_scope = scope

        return scope

    def get_scoped_queryset(
        self,
        request: Request,
        queryset: QuerySet,
    ) -> QuerySet:
        if not self.professional_school_lookup:
            raise ImproperlyConfigured(
                f'{type(self).__name__} debe definir professional_school_lookup.'
            )

        scope = self.get_administration_scope(
            request,
        )

        if scope.is_global:
            return queryset

        return queryset.filter(
            **{
                self.professional_school_lookup: (scope.professional_school_id),
            }
        )

    def get_write_serializer_context(
        self,
        request: Request,
    ) -> dict[str, object]:
        scope = self.get_administration_scope(
            request,
        )

        return {
            'request': request,
            'professional_school_id': (scope.professional_school_id),
        }
