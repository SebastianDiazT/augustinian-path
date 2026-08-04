from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User


class ProfessionalSchoolCatalogListTests(
    APITestCase,
):
    endpoint = '/api/v1/academics/professional-schools/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante.escuelas@unsa.edu.pe',
            password='Prueba123!',
        )

        self.faculty_a = Faculty.objects.create(
            name='Facultad A',
        )
        self.faculty_b = Faculty.objects.create(
            name='Facultad B',
        )
        inactive_faculty = Faculty.objects.create(
            name='Facultad C Inactiva',
            is_active=False,
        )

        self.school_a = ProfessionalSchool.objects.create(
            faculty=self.faculty_a,
            name='Escuela A',
        )
        self.school_b = ProfessionalSchool.objects.create(
            faculty=self.faculty_b,
            name='Escuela B',
        )
        ProfessionalSchool.objects.create(
            faculty=self.faculty_a,
            name='Escuela Inactiva',
            is_active=False,
        )
        ProfessionalSchool.objects.create(
            faculty=inactive_faculty,
            name='Escuela con Facultad Inactiva',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_only_active_school_hierarchy(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        schools = response.json()['data']['professional_schools']

        self.assertEqual(
            [school['name'] for school in schools],
            [
                'Escuela A',
                'Escuela B',
            ],
        )
        self.assertEqual(
            schools[0]['faculty']['id'],
            str(self.faculty_a.public_id),
        )
        self.assertNotIn('is_active', schools[0])

    def test_filters_by_faculty(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'{self.endpoint}?faculty={self.faculty_b.public_id}'
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
                'Escuela B',
            ],
        )

    def test_searches_by_school_name(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?search=escuela b')

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
                'Escuela B',
            ],
        )

    def test_rejects_invalid_faculty_uuid(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?faculty=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'faculty',
            response.json()['error']['errors'],
        )

    def test_paginates_schools(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=1')

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
            data['pagination']['total_items'],
            2,
        )
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])

    def test_rejects_write_requests(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.endpoint,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
