from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CurrentUserEndpointTests(APITestCase):
    endpoint = '/api/v1/auth/me/'

    def authenticate_with_jwt(self, user: User) -> str:  # type: ignore
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
        )

        return access_token

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn(
            'error',
            response.json(),
        )

    def test_returns_authenticated_user(self) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password='Prueba123!',
            first_name='Sebastian',
            last_name='Diaz',
        )

        student_group = Group.objects.get(name='student')
        user.groups.add(student_group)

        self.authenticate_with_jwt(user)

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
                'avatar_url': None,
                'roles': ['student'],
            },
        )

    def test_returns_user_avatar_url(self) -> None:
        avatar_url = 'https://lh3.googleusercontent.com/a/example-google-avatar'

        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password='Prueba123!',
            first_name='Sebastian',
            last_name='Diaz',
            avatar_url=avatar_url,
        )

        self.authenticate_with_jwt(user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['avatar_url'],
            avatar_url,
        )

    def test_returns_null_when_user_has_no_avatar(self) -> None:
        user = User.objects.create_user(
            email='estudiante@unsa.edu.pe',
            password='Prueba123!',
            avatar_url='',
        )

        self.authenticate_with_jwt(user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIsNone(
            response.json()['data']['avatar_url'],
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

        self.authenticate_with_jwt(user)

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

    def test_does_not_accept_session_authentication(
        self,
    ) -> None:
        User.objects.create_user(
            email='sesion@unsa.edu.pe',
            password='Prueba123!',
        )

        logged_in = self.client.login(
            email='sesion@unsa.edu.pe',
            password='Prueba123!',
        )

        self.assertTrue(logged_in)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_rejects_invalid_access_token(self) -> None:
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer invalid-token',
        )

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertIn(
            'error',
            response.json(),
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
