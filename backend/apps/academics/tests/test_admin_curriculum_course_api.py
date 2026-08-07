from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    Course,
    CurriculumCourse,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminCurriculumCourseListTests(
    APITestCase,
):
    endpoint = '/api/v1/admin/curriculum-courses/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.malla@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.malla@unsa.edu.pe',
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

        self.industrial_plan = CurriculumPlan.objects.create(
            professional_school=self.industrial,
            code='2024',
            name='Plan Industrial 2024',
        )
        self.systems_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2025',
            name='Plan Sistemas 2025',
        )

        self.industrial_course = Course.objects.create(
            professional_school=self.industrial,
            code='IN 101',
            name='Introduccion a Industrial',
        )
        self.programming = Course.objects.create(
            professional_school=self.systems,
            code='CS 101',
            name='Programacion',
        )
        self.data_structures = Course.objects.create(
            professional_school=self.systems,
            code='CS 201',
            name='Estructuras de Datos',
        )

        self.industrial_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.industrial_plan,
            course=self.industrial_course,
            cycle=1,
            credits=Decimal('3.00'),
        )
        self.programming_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.systems_plan,
            course=self.programming,
            cycle=1,
            credits=Decimal('4.00'),
        )
        self.data_structures_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.systems_plan,
            course=self.data_structures,
            cycle=2,
            credits=Decimal('4.50'),
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

    def test_returns_curriculum_courses(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        entries = response.json()['data']['curriculum_courses']

        self.assertEqual(
            [entry['course']['code'] for entry in entries],
            [
                'IN 101',
                'CS 101',
                'CS 201',
            ],
        )
        self.assertEqual(
            entries[0]['id'],
            str(self.industrial_entry.public_id),
        )
        self.assertEqual(
            entries[0]['credits'],
            '3.00',
        )
        self.assertEqual(
            entries[0]['curriculum_plan']['id'],
            str(self.industrial_plan.public_id),
        )

    def test_paginates_curriculum_courses(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            len(data['curriculum_courses']),
            1,
        )
        self.assertEqual(
            data['pagination']['total_items'],
            3,
        )
        self.assertFalse(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])

    def test_searches_by_course_code_or_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=ESTRUCTURAS')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                entry['course']['code']
                for entry in response.json()['data']['curriculum_courses']
            ],
            [
                'CS 201',
            ],
        )

    def test_filters_by_curriculum_plan(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?curriculum_plan={self.systems_plan.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                entry['course']['code']
                for entry in response.json()['data']['curriculum_courses']
            ],
            [
                'CS 101',
                'CS 201',
            ],
        )

    def test_filters_by_professional_school(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.systems.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.json()['data']['curriculum_courses']),
            2,
        )

    def test_filters_by_cycle(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?cycle=1')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [
                entry['course']['code']
                for entry in response.json()['data']['curriculum_courses']
            ],
            [
                'IN 101',
                'CS 101',
            ],
        )

    def test_rejects_invalid_plan_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?curriculum_plan=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'curriculum_plan',
            response.json()['error']['errors'],
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

    def test_rejects_put_requests(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            self.endpoint,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
