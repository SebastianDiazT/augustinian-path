from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):
    message = 'Se requiere rol de administrador de plataforma.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_platform_admin
        )


class IsSchoolDelegate(BasePermission):
    message = 'No eres delegado de la escuela asociada a este recurso.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'get_school'):
            school = obj.get_school()
        else:
            school = getattr(obj, 'school', None)
        if school is None:
            return False
        return request.user.is_delegate_of(school)


def student_has_verified_membership(user, school):
    if not hasattr(user, 'student_profile'):
        return False
    return user.student_profile.memberships.filter(
        school=school,
        is_active=True,
    ).exists()


class IsOwnerStudent(BasePermission):
    message = 'Este recurso no te pertenece.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        student = getattr(obj, 'student', None)
        if student is None:
            return False
        return student.user_id == request.user.id
