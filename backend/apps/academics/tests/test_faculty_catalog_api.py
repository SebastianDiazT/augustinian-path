from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty
from apps.accounts.models import User


class FacultyCatalogListTests(APITestCase):
    endpoint = '/api/v1/academics/faculties/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante.catalogo@unsa.edu.pe',
            password='Prueba123!',
        )

        self.engineering = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.medicine = Faculty.objects.create(
            name='Facultad de Medicina',
        )
        Faculty.objects.create(
            name='Facultad Inactiva',
            is_active=False,
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_returns_only_active_faculties(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [faculty['name'] for faculty in response.json()['data']['faculties']],
            [
                'Facultad de Ingenieria',
                'Facultad de Medicina',
            ],
        )
        self.assertNotIn(
            'is_active',
            response.json()['data']['faculties'][0],
        )

    def test_searches_faculties_by_name(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?search=medicina')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [faculty['name'] for faculty in response.json()['data']['faculties']],
            [
                'Facultad de Medicina',
            ],
        )

    def test_paginates_faculties(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=1')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            len(data['faculties']),
            1,
        )
        self.assertEqual(
            data['pagination']['total_items'],
            2,
        )
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])

    def test_rejects_write_requests(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.endpoint,
            {
                'name': 'Facultad no autorizada',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
