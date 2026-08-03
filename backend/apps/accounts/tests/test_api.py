from django.contrib.auth import get_user_model
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

        self.client.force_authenticate(user=user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.json()['data'],
            {
                'id': user.id,
                'email': 'estudiante@unsa.edu.pe',
                'first_name': 'Sebastian',
                'last_name': 'Diaz',
            },
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
