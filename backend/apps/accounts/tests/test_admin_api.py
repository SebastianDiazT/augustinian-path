from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminAccessEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/access/'

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn('error', response.json())

    def test_rejects_student_user(self) -> None:
        user = User.objects.create_user(
            email='solo.estudiante@unsa.edu.pe',
            password='Prueba123!',
        )
        user.groups.add(
            Group.objects.get(
                name=Role.STUDENT.value,
            )
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            response.json()['error']['detail'],
            'No tienes permisos de administración de la plataforma.',
        )

    def test_accepts_platform_admin_user(self) -> None:
        user = User.objects.create_user(
            email='admin.endpoint@unsa.edu.pe',
            password='Prueba123!',
        )
        user.groups.add(
            Group.objects.get(
                name=Role.PLATFORM_ADMIN.value,
            )
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data'],
            {
                'authorized': True,
            },
        )
