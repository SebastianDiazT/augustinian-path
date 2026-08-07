from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    Course,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User


class CourseCatalogListTests(APITestCase):
    endpoint = '/api/v1/academics/courses/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante.asignaturas@unsa.edu.pe',
            password='Prueba123!',
        )

        active_faculty = Faculty.objects.create(
            name='Facultad Activa',
        )
        inactive_faculty = Faculty.objects.create(
            name='Facultad Inactiva',
            is_active=False,
        )

        self.school_a = ProfessionalSchool.objects.create(
            faculty=active_faculty,
            name='Escuela A',
        )
        self.school_b = ProfessionalSchool.objects.create(
            faculty=active_faculty,
            name='Escuela B',
        )
        inactive_school = ProfessionalSchool.objects.create(
            faculty=active_faculty,
            name='Escuela Inactiva',
            is_active=False,
        )
        school_with_inactive_faculty = ProfessionalSchool.objects.create(
            faculty=inactive_faculty,
            name='Escuela con Facultad Inactiva',
        )

        self.course_a = Course.objects.create(
            professional_school=self.school_a,
            code='CS 101',
            name='Programacion',
        )
        self.course_b = Course.objects.create(
            professional_school=self.school_b,
            code='IN 101',
            name='Introduccion a Industrial',
        )
        Course.objects.create(
            professional_school=self.school_a,
            code='CS 102',
            name='Asignatura Inactiva',
            is_active=False,
        )
        Course.objects.create(
            professional_school=inactive_school,
            code='XX 101',
            name='Asignatura de Escuela Inactiva',
        )
        Course.objects.create(
            professional_school=(school_with_inactive_faculty),
            code='YY 101',
            name='Asignatura de Facultad Inactiva',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_returns_only_active_course_hierarchy(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        courses = response.json()['data']['courses']

        self.assertEqual(
            [course['code'] for course in courses],
            [
                'CS 101',
                'IN 101',
            ],
        )
        self.assertEqual(
            courses[0]['professional_school']['id'],
            str(self.school_a.public_id),
        )
        self.assertNotIn('is_active', courses[0])

    def test_filters_by_professional_school(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.school_b.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [course['code'] for course in response.json()['data']['courses']],
            [
                'IN 101',
            ],
        )

    def test_searches_by_code_or_name(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?search=programacion')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [course['code'] for course in response.json()['data']['courses']],
            [
                'CS 101',
            ],
        )

    def test_rejects_invalid_school_uuid(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?professional_school=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'professional_school',
            response.json()['error']['errors'],
        )

    def test_paginates_courses(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=1')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            len(data['courses']),
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
