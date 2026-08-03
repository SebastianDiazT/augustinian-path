from typing import Any

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import (
    BaseCommand,
    CommandError,
    CommandParser,
)
from django.db import transaction

from apps.accounts.models import User
from apps.accounts.roles import Role
from apps.accounts.validators import validate_institutional_email


class Command(BaseCommand):
    help = 'Asigna o retira el rol platform_admin por correo institucional.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'email',
            help='Correo institucional del usuario existente.',
        )

        action_group = parser.add_mutually_exclusive_group(
            required=True,
        )
        action_group.add_argument(
            '--grant',
            action='store_true',
            help='Asigna el rol platform_admin.',
        )
        action_group.add_argument(
            '--revoke',
            action='store_true',
            help='Retira el rol platform_admin.',
        )

    @transaction.atomic
    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        grant = bool(options['grant'])
        revoke = bool(options['revoke'])

        if grant == revoke:
            raise CommandError(
                'Debes indicar exactamente una acción: --grant o --revoke.'
            )

        normalized_email = User.objects.normalize_email(
            str(options['email']).strip()
        ).lower()

        try:
            validate_institutional_email(normalized_email)
        except ValidationError as error:
            raise CommandError(
                'El correo debe pertenecer al dominio institucional @unsa.edu.pe.'
            ) from error

        try:
            admin_group = Group.objects.select_for_update().get(
                name=Role.PLATFORM_ADMIN.value,
            )
        except Group.DoesNotExist as error:
            raise CommandError(
                'No existe el grupo platform_admin. Ejecuta las migraciones pendientes.'
            ) from error

        try:
            user = User.objects.select_for_update().get(
                email=normalized_email,
            )
        except User.DoesNotExist as error:
            raise CommandError(
                f'No existe un usuario con el correo {normalized_email}.'
            ) from error

        if grant:
            self._grant_role(user, admin_group)
            return

        self._revoke_role(user, admin_group)

    def _grant_role(
        self,
        user: User,
        admin_group: Group,
    ) -> None:
        if not user.is_active:
            raise CommandError(
                'No se puede asignar platform_admin a una cuenta inactiva.'
            )

        if user.groups.filter(pk=admin_group.pk).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'{user.email} ya tiene el rol platform_admin. '
                    'No se realizaron cambios.'
                )
            )
            return

        user.groups.add(admin_group)

        self.stdout.write(
            self.style.SUCCESS(f'Rol platform_admin asignado a {user.email}.')
        )

    def _revoke_role(
        self,
        user: User,
        admin_group: Group,
    ) -> None:
        if not user.groups.filter(pk=admin_group.pk).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'{user.email} no tiene el rol platform_admin. '
                    'No se realizaron cambios.'
                )
            )
            return

        if user.is_active:
            other_active_admin_exists = (
                User.objects.filter(
                    groups=admin_group,
                    is_active=True,
                )
                .exclude(pk=user.pk)
                .exists()
            )

            if not other_active_admin_exists:
                raise CommandError(
                    'No se puede retirar el rol al último '
                    'administrador activo. Asigna otro primero.'
                )

        user.groups.remove(admin_group)

        self.stdout.write(
            self.style.SUCCESS(f'Rol platform_admin retirado de {user.email}.')
        )
