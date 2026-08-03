from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .roles import Role


class IsPlatformAdmin(BasePermission):
    message = 'No tienes permisos de administración de la plataforma.'
    code = 'platform_admin_required'

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(
                name=Role.PLATFORM_ADMIN.value,
            ).exists()
        )
