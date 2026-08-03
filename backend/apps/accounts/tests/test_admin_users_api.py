from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminUserListEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/users/'

    def setUp(self) -> None:
        self.admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        self.student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.lista@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(
            self.admin_group,
            self.student_group,
        )

        self.student = User.objects.create_user(
            email='estudiante.lista@unsa.edu.pe',
            password='Prueba123!',
            first_name='Ana',
            last_name='Torres',
        )
        self.student.groups.add(self.student_group)

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertIn('error', response.json())

    def test_rejects_student_user(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            response.json()['error']['detail'],
            'No tienes permisos de administración de la plataforma.',
        )

    def test_returns_users_ordered_by_email(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        users = response.json()['data']['users']

        self.assertEqual(
            [user['email'] for user in users],
            [
                'admin.lista@unsa.edu.pe',
                'estudiante.lista@unsa.edu.pe',
            ],
        )

        admin_data = users[0]

        self.assertEqual(
            admin_data['id'],
            str(self.admin.public_id),
        )
        self.assertEqual(
            admin_data['roles'],
            [
                'platform_admin',
                'student',
            ],
        )
        self.assertNotIn('password', admin_data)
        self.assertNotIn('is_staff', admin_data)
        self.assertNotIn('is_superuser', admin_data)

    def test_paginates_users(self) -> None:
        for index in range(3):
            User.objects.create_user(
                email=f'usuario{index}@unsa.edu.pe',
                password='Prueba123!',
            )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(len(data['users']), 2)
        self.assertEqual(
            data['pagination'],
            {
                'page': 2,
                'page_size': 2,
                'total_items': 5,
                'total_pages': 3,
                'has_next': True,
                'has_previous': True,
            },
        )

    def test_searches_by_email_or_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=TORRES')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [user['email'] for user in response.json()['data']['users']],
            [
                'estudiante.lista@unsa.edu.pe',
            ],
        )

    def test_filters_by_role(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?role=platform_admin')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [user['email'] for user in response.json()['data']['users']],
            [
                'admin.lista@unsa.edu.pe',
            ],
        )

    def test_filters_by_active_status(self) -> None:
        self.student.is_active = False
        self.student.save(update_fields=['is_active'])

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?is_active=false')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [user['email'] for user in response.json()['data']['users']],
            [
                'estudiante.lista@unsa.edu.pe',
            ],
        )

    def test_combines_filters_before_pagination(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            self.endpoint
            + '?search=ana'
            + '&role=student'
            + '&is_active=true'
            + '&page_size=1'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            [user['email'] for user in data['users']],
            [
                'estudiante.lista@unsa.edu.pe',
            ],
        )
        self.assertEqual(
            data['pagination'],
            {
                'page': 1,
                'page_size': 1,
                'total_items': 1,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False,
            },
        )

    def test_rejects_unknown_role_filter(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?role=unknown')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'role',
            response.json()['error']['errors'],
        )
