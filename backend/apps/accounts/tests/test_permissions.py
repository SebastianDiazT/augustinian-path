from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.permissions import IsPlatformAdmin
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
