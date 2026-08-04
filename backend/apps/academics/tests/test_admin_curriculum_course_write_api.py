from decimal import Decimal
from uuid import uuid4

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


class PlatformAdminCurriculumCourseWriteTests(
    APITestCase,
):
    endpoint = '/api/v1/admin/curriculum-courses/'

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email='admin.malla.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(
            Group.objects.get(
                name=Role.PLATFORM_ADMIN.value,
            )
        )

        self.student = User.objects.create_user(
            email='estudiante.malla.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            Group.objects.get(
                name=Role.STUDENT.value,
            )
        )

        faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Escuela Profesional de Sistemas',
        )
        self.industrial = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Escuela Profesional de Industrial',
        )

        self.systems_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2025',
            name='Plan Sistemas 2025',
        )
        self.industrial_plan = CurriculumPlan.objects.create(
            professional_school=self.industrial,
            code='2024',
            name='Plan Industrial 2024',
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
        self.industrial_course = Course.objects.create(
            professional_school=self.industrial,
            code='IN 101',
            name='Introduccion a Industrial',
        )

        self.entry = CurriculumCourse.objects.create(
            curriculum_plan=self.systems_plan,
            course=self.programming,
            cycle=1,
            credits=Decimal('4.00'),
        )

    def valid_payload(self) -> dict[str, object]:
        return {
            'curriculum_plan_id': str(self.systems_plan.public_id),
            'course_id': str(self.data_structures.public_id),
            'cycle': 2,
            'credits': '4.50',
        }

    def detail_endpoint(
        self,
        entry: CurriculumCourse,
    ) -> str:
        return f'{self.endpoint}{entry.public_id}/'

    def test_rejects_unauthenticated_create(self) -> None:
        response = self.client.post(
            self.endpoint,
            self.valid_payload(),
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_student_create(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.endpoint,
            self.valid_payload(),
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creates_curriculum_course(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.endpoint,
            self.valid_payload(),
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        created_entry = CurriculumCourse.objects.get(
            public_id=response.json()['data']['id'],
        )

        self.assertEqual(
            created_entry.curriculum_plan,
            self.systems_plan,
        )
        self.assertEqual(
            created_entry.course,
            self.data_structures,
        )
        self.assertEqual(created_entry.cycle, 2)
        self.assertEqual(
            created_entry.credits,
            Decimal('4.50'),
        )

    def test_rejects_unknown_curriculum_plan(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['curriculum_plan_id'] = str(uuid4())

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'curriculum_plan_id',
            response.json()['error']['errors'],
        )

    def test_rejects_unknown_course(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['course_id'] = str(uuid4())

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_rejects_course_from_another_school(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['course_id'] = str(self.industrial_course.public_id)

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_rejects_duplicate_course_in_plan(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['course_id'] = str(self.programming.public_id)

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_rejects_cycle_below_one(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['cycle'] = 0

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'cycle',
            response.json()['error']['errors'],
        )

    def test_rejects_negative_credits(self) -> None:
        self.client.force_authenticate(user=self.admin)

        payload = self.valid_payload()
        payload['credits'] = '-0.01'

        response = self.client.post(
            self.endpoint,
            payload,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'credits',
            response.json()['error']['errors'],
        )

    def test_updates_cycle_and_credits(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint(self.entry),
            {
                'cycle': 3,
                'credits': '5.25',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.entry.refresh_from_db()

        self.assertEqual(self.entry.cycle, 3)
        self.assertEqual(
            self.entry.credits,
            Decimal('5.25'),
        )
        self.assertEqual(
            response.json()['data']['credits'],
            '5.25',
        )

    def test_rejects_curriculum_plan_change(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint(self.entry),
            {
                'curriculum_plan_id': str(self.industrial_plan.public_id),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'curriculum_plan_id',
            response.json()['error']['errors'],
        )

    def test_rejects_course_change(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint(self.entry),
            {
                'course_id': str(self.data_structures.public_id),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'course_id',
            response.json()['error']['errors'],
        )

    def test_rejects_student_update(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.patch(
            self.detail_endpoint(self.entry),
            {
                'cycle': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_not_found_for_unknown_entry(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'{self.endpoint}{uuid4()}/',
            {
                'cycle': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_rejects_empty_patch(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint(self.entry),
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rejects_delete(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            self.detail_endpoint(self.entry),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
