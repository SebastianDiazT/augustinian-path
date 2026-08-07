from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    Course,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminCourseListTests(APITestCase):
    endpoint = '/api/v1/admin/courses/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.cursos@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.cursos@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.industrial = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Industrial',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.industrial_course = Course.objects.create(
            professional_school=self.industrial,
            code='IN 101',
            name='Introduccion a Industrial',
        )
        self.old_systems_course = Course.objects.create(
            professional_school=self.systems,
            code='CS 101',
            name='Programacion',
            is_active=False,
        )
        self.current_systems_course = Course.objects.create(
            professional_school=self.systems,
            code='CS 201',
            name='Estructuras de Datos',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_rejects_student_user(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_courses_ordered_by_school_and_code(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        courses = response.json()['data']['courses']

        self.assertEqual(
            [course['code'] for course in courses],
            [
                'IN 101',
                'CS 101',
                'CS 201',
            ],
        )
        self.assertEqual(
            courses[0]['id'],
            str(self.industrial_course.public_id),
        )
        self.assertEqual(
            courses[0]['professional_school']['id'],
            str(self.industrial.public_id),
        )
        self.assertEqual(
            courses[0]['professional_school']['faculty']['id'],
            str(self.faculty.public_id),
        )

    def test_paginates_courses(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(len(data['courses']), 1)
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

    def test_searches_courses_by_code_or_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=PROGRAMACION')

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

    def test_filters_courses_by_school_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.systems.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [course['code'] for course in response.json()['data']['courses']],
            [
                'CS 101',
                'CS 201',
            ],
        )

    def test_rejects_invalid_school_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?professional_school=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'professional_school',
            response.json()['error']['errors'],
        )

    def test_filters_courses_by_active_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?is_active=false')

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

    def test_rejects_put_requests(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            self.endpoint,
            {
                'code': 'CS 999',
                'name': 'Curso no permitido',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
