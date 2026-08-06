from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase

from apps.academics.models import Faculty, ProfessionalSchool
from apps.accounts.models import AcademicAdminAssignment, User
from apps.accounts.permissions import (
    IsAcademicAdmin,
    IsPlatformAdmin,
    IsPlatformOrAcademicAdmin,
)
from apps.accounts.roles import Role


class IsPlatformAdminTests(TestCase):
    def setUp(self) -> None:
        self.permission = IsPlatformAdmin()
        self.view = SimpleNamespace()

    def test_rejects_anonymous_user(self) -> None:
        request = SimpleNamespace(
            user=AnonymousUser(),
        )

        self.assertFalse(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_rejects_student_user(self) -> None:
        user = User.objects.create_user(
            email='estudiante.permiso@unsa.edu.pe',
            password='Prueba123!',
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )
        user.groups.add(student_group)

        request = SimpleNamespace(user=user)

        self.assertFalse(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_accepts_platform_admin_user(self) -> None:
        user = User.objects.create_user(
            email='admin.plataforma@unsa.edu.pe',
            password='Prueba123!',
        )
        user.groups.add(
            Group.objects.get(
                name=Role.STUDENT.value,
            ),
            Group.objects.get(
                name=Role.PLATFORM_ADMIN.value,
            ),
        )

        request = SimpleNamespace(user=user)

        self.assertTrue(
            self.permission.has_permission(
                request,
                self.view,
            )
        )


class IsAcademicAdminTests(TestCase):
    def setUp(self) -> None:
        self.permission = IsAcademicAdmin()
        self.view = SimpleNamespace()
        self.user = User.objects.create_user(
            email='admin.academico@unsa.edu.pe',
            password='Prueba123!',
        )
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Ingeniería de Sistemas',
        )

    def test_rejects_user_without_academic_admin_role(self) -> None:
        AcademicAdminAssignment.objects.create(
            user=self.user,
            professional_school=self.school,
        )

        request = SimpleNamespace(user=self.user)

        self.assertFalse(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_rejects_academic_admin_without_assignment(self) -> None:
        self.user.groups.add(
            Group.objects.get(
                name=Role.ACADEMIC_ADMIN.value,
            )
        )

        request = SimpleNamespace(user=self.user)

        self.assertFalse(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_accepts_academic_admin_with_active_school(self) -> None:
        self.user.groups.add(
            Group.objects.get(
                name=Role.ACADEMIC_ADMIN.value,
            )
        )
        AcademicAdminAssignment.objects.create(
            user=self.user,
            professional_school=self.school,
        )

        request = SimpleNamespace(user=self.user)

        self.assertTrue(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_rejects_assignment_to_inactive_school(self) -> None:
        self.user.groups.add(
            Group.objects.get(
                name=Role.ACADEMIC_ADMIN.value,
            )
        )
        AcademicAdminAssignment.objects.create(
            user=self.user,
            professional_school=self.school,
        )
        self.school.is_active = False
        self.school.save(
            update_fields=['is_active'],
        )

        request = SimpleNamespace(user=self.user)

        self.assertFalse(
            self.permission.has_permission(
                request,
                self.view,
            )
        )


class IsPlatformOrAcademicAdminTests(TestCase):
    def setUp(self) -> None:
        self.permission = IsPlatformOrAcademicAdmin()
        self.view = SimpleNamespace()

    def test_accepts_platform_admin(self) -> None:
        user = User.objects.create_user(
            email='admin.global@unsa.edu.pe',
            password='Prueba123!',
        )
        user.groups.add(
            Group.objects.get(
                name=Role.PLATFORM_ADMIN.value,
            )
        )

        request = SimpleNamespace(user=user)

        self.assertTrue(
            self.permission.has_permission(
                request,
                self.view,
            )
        )

    def test_accepts_scoped_academic_admin(self) -> None:
        faculty = Faculty.objects.create(
            name='Facultad de Ciencias',
        )
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ciencia de la Computación',
        )
        user = User.objects.create_user(
            email='admin.ciencias@unsa.edu.pe',
            password='Prueba123!',
        )
        user.groups.add(
            Group.objects.get(
                name=Role.ACADEMIC_ADMIN.value,
            )
        )
        AcademicAdminAssignment.objects.create(
            user=user,
            professional_school=school,
        )

        request = SimpleNamespace(user=user)

        self.assertTrue(
            self.permission.has_permission(
                request,
                self.view,
            )
        )
