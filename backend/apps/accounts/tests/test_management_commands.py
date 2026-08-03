from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.roles import Role


class ManagePlatformAdminCommandTests(TestCase):
    command_name = 'manage_platform_admin'

    def setUp(self) -> None:
        self.admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        self.user = User.objects.create_user(
            email='admin.nuevo@unsa.edu.pe',
            password='Prueba123!',
        )

    def run_command(
        self,
        email: str,
        **options: bool,
    ) -> str:
        output = StringIO()

        call_command(
            self.command_name,
            email,
            stdout=output,
            **options,
        )

        return output.getvalue()

    def test_grants_role_using_normalized_email(self) -> None:
        output = self.run_command(
            '  ADMIN.NUEVO@UNSA.EDU.PE  ',
            grant=True,
        )

        self.assertTrue(
            self.user.groups.filter(
                pk=self.admin_group.pk,
            ).exists()
        )
        self.assertIn('asignado', output)

    def test_rejects_non_institutional_email(self) -> None:
        with self.assertRaisesMessage(
            CommandError,
            '@unsa.edu.pe',
        ):
            self.run_command(
                'persona@gmail.com',
                grant=True,
            )

    def test_rejects_unknown_user(self) -> None:
        with self.assertRaisesMessage(
            CommandError,
            'No existe un usuario',
        ):
            self.run_command(
                'no.existe@unsa.edu.pe',
                grant=True,
            )

    def test_rejects_grant_for_inactive_user(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        with self.assertRaisesMessage(
            CommandError,
            'cuenta inactiva',
        ):
            self.run_command(
                self.user.email,
                grant=True,
            )

    def test_grant_is_idempotent(self) -> None:
        self.user.groups.add(self.admin_group)

        output = self.run_command(
            self.user.email,
            grant=True,
        )

        self.assertEqual(
            self.user.groups.filter(
                pk=self.admin_group.pk,
            ).count(),
            1,
        )
        self.assertIn('ya tiene', output)

    def test_revokes_role_when_another_active_admin_exists(
        self,
    ) -> None:
        other_admin = User.objects.create_user(
            email='otro.admin@unsa.edu.pe',
            password='Prueba123!',
        )
        self.user.groups.add(self.admin_group)
        other_admin.groups.add(self.admin_group)

        output = self.run_command(
            self.user.email,
            revoke=True,
        )

        self.assertFalse(
            self.user.groups.filter(
                pk=self.admin_group.pk,
            ).exists()
        )
        self.assertTrue(
            other_admin.groups.filter(
                pk=self.admin_group.pk,
            ).exists()
        )
        self.assertIn('retirado', output)

    def test_refuses_to_revoke_last_active_admin(self) -> None:
        self.user.groups.add(self.admin_group)

        with self.assertRaisesMessage(
            CommandError,
            'último administrador activo',
        ):
            self.run_command(
                self.user.email,
                revoke=True,
            )

        self.assertTrue(
            self.user.groups.filter(
                pk=self.admin_group.pk,
            ).exists()
        )

    def test_revoke_is_idempotent_without_role(self) -> None:
        output = self.run_command(
            self.user.email,
            revoke=True,
        )

        self.assertFalse(
            self.user.groups.filter(
                pk=self.admin_group.pk,
            ).exists()
        )
        self.assertIn('no tiene', output)
