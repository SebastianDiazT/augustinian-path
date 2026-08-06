from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import AcademicAdminAssignment
from .roles import Role


def user_has_role(
    request: Request,
    role: Role,
) -> bool:
    user = request.user

    return bool(
        user
        and user.is_authenticated
        and user.groups.filter(
            name=role.value,
        ).exists()
    )


class IsPlatformAdmin(BasePermission):
    message = 'No tienes permisos de administración de la plataforma.'
    code = 'platform_admin_required'

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        return user_has_role(
            request,
            Role.PLATFORM_ADMIN,
        )


class IsAcademicAdmin(BasePermission):
    message = 'No tienes permisos de administración académica.'
    code = 'academic_admin_required'

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        if not user_has_role(
            request,
            Role.ACADEMIC_ADMIN,
        ):
            return False

        return AcademicAdminAssignment.objects.filter(
            user=request.user,
            professional_school__is_active=True,
        ).exists()


class IsStudent(BasePermission):
    message = 'No tienes permisos de estudiante.'
    code = 'student_required'

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        return user_has_role(
            request,
            Role.STUDENT,
        )


class IsPlatformOrAcademicAdmin(BasePermission):
    message = 'No tienes permisos de administración académica.'
    code = 'admin_required'

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        return IsPlatformAdmin().has_permission(
            request,
            view,
        ) or IsAcademicAdmin().has_permission(
            request,
            view,
        )
