from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminCurriculumPlanListTests(APITestCase):
    endpoint = '/api/v1/admin/curriculum-plans/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.planes@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.planes@unsa.edu.pe',
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
            name='Plan de Estudios 2024',
        )
        self.old_systems_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2017',
            name='Plan de Estudios 2017',
            is_active=False,
        )
        self.current_systems_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2025',
            name='Plan de Estudios 2025',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_student_user(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_plans_ordered_by_school_and_code(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        plans = response.json()['data']['curriculum_plans']

        self.assertEqual(
            [plan['code'] for plan in plans],
            [
                '2024',
                '2017',
                '2025',
            ],
        )
        self.assertEqual(
            plans[0]['id'],
            str(self.industrial_plan.public_id),
        )
        self.assertEqual(
            plans[0]['professional_school']['id'],
            str(self.industrial.public_id),
        )
        self.assertEqual(
            plans[0]['professional_school']['faculty']['id'],
            str(self.faculty.public_id),
        )

    def test_paginates_plans(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=2')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()['data']

        self.assertEqual(
            len(data['curriculum_plans']),
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

    def test_searches_plans_by_code_or_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?search=2025')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [plan['code'] for plan in response.json()['data']['curriculum_plans']],
            [
                '2025',
            ],
        )

    def test_filters_plans_by_school_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.systems.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [plan['code'] for plan in response.json()['data']['curriculum_plans']],
            [
                '2017',
                '2025',
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

    def test_filters_plans_by_active_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f'{self.endpoint}?is_active=false')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [plan['code'] for plan in response.json()['data']['curriculum_plans']],
            [
                '2017',
            ],
        )

    def test_rejects_write_requests(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.endpoint,
            {
                'code': '2030',
                'name': 'Plan no permitido',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
