from django.contrib.auth.models import Group
from django.test import TestCase

from apps.accounts.roles import Role


class InitialRoleGroupsTests(TestCase):
    def test_initial_role_groups_exist(self) -> None:
        expected_roles = {role.value for role in Role}

        existing_roles = set(
            Group.objects.filter(
                name__in=expected_roles,
            ).values_list(
                'name',
                flat=True,
            )
        )

        self.assertEqual(
            existing_roles,
            expected_roles,
        )
