from django.contrib.auth.models import Group
from django.db import transaction

from apps.academics.models import ProfessionalSchool

from .models import AcademicAdminAssignment, User
from .roles import Role


@transaction.atomic
def assign_academic_admin(
    *,
    user: User,
    professional_school: ProfessionalSchool,
) -> User:
    locked_user = User.objects.select_for_update().get(
        pk=user.pk,
    )
    locked_school = ProfessionalSchool.objects.select_for_update().get(
        pk=professional_school.pk,
        is_active=True,
    )

    AcademicAdminAssignment.objects.update_or_create(
        user=locked_user,
        defaults={
            'professional_school': locked_school,
        },
    )

    academic_admin_group = Group.objects.get(
        name=Role.ACADEMIC_ADMIN.value,
    )
    locked_user.groups.add(academic_admin_group)

    return locked_user


@transaction.atomic
def remove_academic_admin(
    *,
    user: User,
) -> User:
    locked_user = User.objects.select_for_update().get(
        pk=user.pk,
    )

    AcademicAdminAssignment.objects.filter(
        user=locked_user,
    ).delete()

    academic_admin_group = Group.objects.get(
        name=Role.ACADEMIC_ADMIN.value,
    )
    locked_user.groups.remove(academic_admin_group)

    return locked_user
