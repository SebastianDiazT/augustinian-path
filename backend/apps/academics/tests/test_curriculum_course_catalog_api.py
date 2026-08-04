from decimal import Decimal

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


class CurriculumCourseCatalogListTests(
    APITestCase,
):
    endpoint = '/api/v1/academics/curriculum-courses/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante.malla.catalogo@unsa.edu.pe',
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

        self.plan_a = CurriculumPlan.objects.create(
            professional_school=self.school_a,
            code='2024',
            name='Plan A',
        )
        self.plan_b = CurriculumPlan.objects.create(
            professional_school=self.school_b,
            code='2025',
            name='Plan B',
        )
        inactive_plan = CurriculumPlan.objects.create(
            professional_school=self.school_a,
            code='2023',
            name='Plan Inactivo',
            is_active=False,
        )

        course_a = Course.objects.create(
            professional_school=self.school_a,
            code='CS 101',
            name='Programacion',
        )
        course_a_two = Course.objects.create(
            professional_school=self.school_a,
            code='CS 201',
            name='Estructuras de Datos',
        )
        course_b = Course.objects.create(
            professional_school=self.school_b,
            code='IN 101',
            name='Introduccion a Industrial',
        )
        inactive_course = Course.objects.create(
            professional_school=self.school_b,
            code='IN 201',
            name='Asignatura Inactiva',
            is_active=False,
        )

        CurriculumCourse.objects.create(
            curriculum_plan=self.plan_a,
            course=course_a,
            cycle=1,
            credits=Decimal('4.00'),
        )
        CurriculumCourse.objects.create(
            curriculum_plan=self.plan_a,
            course=course_a_two,
            cycle=2,
            credits=Decimal('4.50'),
        )
        CurriculumCourse.objects.create(
            curriculum_plan=self.plan_b,
            course=course_b,
            cycle=1,
            credits=Decimal('3.00'),
        )

        CurriculumCourse.objects.create(
            curriculum_plan=inactive_plan,
            course=course_a,
            cycle=1,
            credits=Decimal('4.00'),
        )
        CurriculumCourse.objects.create(
            curriculum_plan=self.plan_b,
            course=inactive_course,
            cycle=2,
            credits=Decimal('3.00'),
        )

        inactive_school_plan = CurriculumPlan.objects.create(
            professional_school=inactive_school,
            code='2022',
            name='Plan de Escuela Inactiva',
        )
        inactive_school_course = Course.objects.create(
            professional_school=inactive_school,
            code='XX 101',
            name='Curso de Escuela Inactiva',
        )
        CurriculumCourse.objects.create(
            curriculum_plan=inactive_school_plan,
            course=inactive_school_course,
            cycle=1,
            credits=Decimal('3.00'),
        )

        inactive_faculty_school_plan = CurriculumPlan.objects.create(
            professional_school=(school_with_inactive_faculty),
            code='2021',
            name='Plan de Facultad Inactiva',
        )
        inactive_faculty_course = Course.objects.create(
            professional_school=(school_with_inactive_faculty),
            code='YY 101',
            name='Curso de Facultad Inactiva',
        )
        CurriculumCourse.objects.create(
            curriculum_plan=(inactive_faculty_school_plan),
            course=inactive_faculty_course,
            cycle=1,
            credits=Decimal('3.00'),
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_only_active_hierarchy(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        entries = response.json()['data']['curriculum_courses']

        self.assertEqual(
            [entry['course']['code'] for entry in entries],
            [
                'CS 101',
                'CS 201',
                'IN 101',
            ],
        )
        self.assertEqual(entries[0]['credits'], '4.00')
        self.assertNotIn(
            'is_active',
            entries[0]['curriculum_plan'],
        )

    def test_filters_by_curriculum_plan(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'{self.endpoint}?curriculum_plan={self.plan_a.public_id}'
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

    def test_filters_by_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)

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
                'CS 101',
                'IN 101',
            ],
        )

    def test_searches_by_course(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?search=estructuras')

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

    def test_rejects_invalid_plan_uuid(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?curriculum_plan=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'curriculum_plan',
            response.json()['error']['errors'],
        )

    def test_rejects_invalid_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?cycle=invalid')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'cycle',
            response.json()['error']['errors'],
        )

    def test_paginates_curriculum_courses(self) -> None:
        self.client.force_authenticate(user=self.user)

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
