from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminFacultyListEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/faculties/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.facultades@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.facultades@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.science_faculty = Faculty.objects.create(
            name='Facultad de Ciencias',
        )
        self.medicine_faculty = Faculty.objects.create(
            name='Facultad de Medicina',
            is_active=False,
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
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

    def test_returns_faculties_ordered_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        faculties = response.json()['data']['faculties']

        self.assertEqual(
            [faculty['name'] for faculty in faculties],
            [
                'Facultad de Ciencias',
                'Facultad de Medicina',
            ],
        )
        self.assertEqual(
            faculties[0]['id'],
            str(self.science_faculty.public_id),
        )
        self.assertNotIn('public_id', faculties[0])

    def test_paginates_faculties(self) -> None:
        Faculty.objects.create(
            name='Facultad de Ingenieria',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(len(data['faculties']), 1)
        self.assertEqual(
            data['pagination'],
            {
                'page': 2,
                'page_size': 2,
                'total_items': 3,
                'total_pages': 2,
                'has_next': False,
                'has_previous': True,
            },
        )

    def test_searches_faculties_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=MEDICINA')

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

    def test_filters_faculties_by_active_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?is_active=false')

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

    def test_rejects_put_requests(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            self.endpoint,
            {
                'name': 'Facultad no permitida',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertIn('error', response.json())

    def test_rejects_page_out_of_range(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?page=999',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            response.json()['error']['status'],
            status.HTTP_404_NOT_FOUND,
        )
        self.assertIn('meta', response.json())
