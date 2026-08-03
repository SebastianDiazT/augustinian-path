from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CurrentUserEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/me/'

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.assertIn('error', response.json())

    def test_returns_authenticated_user(self) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password='Prueba123!',
            first_name='Sebastian',
            last_name='Diaz',
        )

        student_group = Group.objects.get(name='student')
        user.groups.add(student_group)

        self.client.force_authenticate(user=user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.json()['data'],
            {
                'id': str(user.public_id),
                'email': 'estudiante@unsa.edu.pe',
                'first_name': 'Sebastian',
                'last_name': 'Diaz',
                'roles': ['student'],
            },
        )

    def test_returns_all_user_roles_ordered_by_name(self) -> None:
        user = User.objects.create_user(
            email='administrador@unsa.edu.pe',
            password='Prueba123!',
        )

        student_group = Group.objects.get(name='student')
        admin_group = Group.objects.get(name='platform_admin')

        user.groups.add(
            student_group,
            admin_group,
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['roles'],
            [
                'platform_admin',
                'student',
            ],
        )


class CSRFEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/csrf/'

    def test_sets_csrf_cookie(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data'],
            {
                'csrf_cookie_set': True,
            },
        )
        self.assertIn('csrftoken', response.cookies)

    def test_is_available_without_authentication(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


class LogoutEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/logout/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='logout@unsa.edu.pe',
            password='Prueba123!',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.post(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertIn('error', response.json())

    def test_logs_out_authenticated_user(self) -> None:
        self.client.login(
            email='logout@unsa.edu.pe',
            password='Prueba123!',
        )

        response = self.client.post(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data'],
            {
                'authenticated': False,
            },
        )

        me_response = self.client.get('/api/v1/auth/me/')

        self.assertEqual(
            me_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
