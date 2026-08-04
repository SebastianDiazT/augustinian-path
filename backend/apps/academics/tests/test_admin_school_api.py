from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty, ProfessionalSchool
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminSchoolListEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/professional-schools/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.escuelas@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.escuelas@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.engineering = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.medicine = Faculty.objects.create(
            name='Facultad de Medicina',
        )

        self.industrial = ProfessionalSchool.objects.create(
            faculty=self.engineering,
            name='Escuela Profesional de Industrial',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=self.engineering,
            name='Escuela Profesional de Sistemas',
        )
        self.medicine_school = ProfessionalSchool.objects.create(
            faculty=self.medicine,
            name='Escuela Profesional de Medicina',
            is_active=False,
        )

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

    def test_returns_schools_ordered_by_faculty_and_name(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        schools = response.json()['data']['professional_schools']

        self.assertEqual(
            [school['name'] for school in schools],
            [
                'Escuela Profesional de Industrial',
                'Escuela Profesional de Sistemas',
                'Escuela Profesional de Medicina',
            ],
        )
        self.assertEqual(
            schools[0]['id'],
            str(self.industrial.public_id),
        )
        self.assertEqual(
            schools[0]['faculty'],
            {
                'id': str(self.engineering.public_id),
                'name': 'Facultad de Ingenieria',
            },
        )

    def test_paginates_schools(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            len(data['professional_schools']),
            1,
        )
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

    def test_searches_schools_by_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=SISTEMAS')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                school['name']
                for school in response.json()['data']['professional_schools']
            ],
            [
                'Escuela Profesional de Sistemas',
            ],
        )

    def test_filters_schools_by_faculty_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?faculty={self.engineering.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                school['name']
                for school in response.json()['data']['professional_schools']
            ],
            [
                'Escuela Profesional de Industrial',
                'Escuela Profesional de Sistemas',
            ],
        )

    def test_rejects_invalid_faculty_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?faculty=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'faculty',
            response.json()['error']['errors'],
        )

    def test_filters_schools_by_active_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?is_active=false')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                school['name']
                for school in response.json()['data']['professional_schools']
            ],
            [
                'Escuela Profesional de Medicina',
            ],
        )

    def test_rejects_put_requests(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            self.endpoint,
            {
                'name': 'Escuela no permitida',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
