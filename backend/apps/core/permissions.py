from rest_framework.permissions import BasePermission

from apps.accounts.models import SchoolDelegation


class IsPlatformAdmin(BasePermission):
    """Acceso exclusivo para el super administrador (tú)."""

    message = 'Se requiere rol de administrador de plataforma.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_platform_admin
        )


class IsAdminOrDelegate(BasePermission):
    """
    Control de acceso dual (Lista y Detalle).
    - Lista: ¿Es admin o delegado de AL MENOS una escuela?
    - Detalle: ¿Es admin o delegado de ESTA escuela en particular?
    """

    message = 'Acceso denegado. Se requiere rol de administrador o delegado de escuela.'

    def has_permission(self, request, view):
        user = request.user
        if not bool(user and user.is_authenticated):
            return False

        if user.is_platform_admin:
            return True

        return SchoolDelegation.objects.filter(delegate=user).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_platform_admin:
            return True

        if hasattr(obj, 'get_school'):
            school = obj.get_school()
        else:
            school = getattr(obj, 'school', None)

        if school is None:
            return False

        return SchoolDelegation.objects.filter(delegate=user, school=school).exists()


class IsOwnerUser(BasePermission):
    """Reemplazo de IsOwnerStudent: Verifica si el usuario logueado es el dueño del recurso."""

    message = 'Este recurso no te pertenece.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None)
        if owner is None:
            return False
        return owner.id == request.user.id
