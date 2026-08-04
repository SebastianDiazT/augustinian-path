from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import User


class CurriculumPlanCatalogListTests(APITestCase):
    endpoint = '/api/v1/academics/curriculum-plans/'

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='estudiante.planes@unsa.edu.pe',
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
        CurriculumPlan.objects.create(
            professional_school=self.school_a,
            code='2023',
            name='Plan Inactivo',
            is_active=False,
        )
        CurriculumPlan.objects.create(
            professional_school=inactive_school,
            code='2022',
            name='Plan de Escuela Inactiva',
        )
        CurriculumPlan.objects.create(
            professional_school=(school_with_inactive_faculty),
            code='2021',
            name='Plan de Facultad Inactiva',
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_only_active_plan_hierarchy(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.user)

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
                '2025',
            ],
        )
        self.assertEqual(
            plans[0]['professional_school']['id'],
            str(self.school_a.public_id),
        )
        self.assertNotIn('is_active', plans[0])

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
            [plan['code'] for plan in response.json()['data']['curriculum_plans']],
            [
                '2025',
            ],
        )

    def test_searches_by_code_or_name(self) -> None:
        self.client.force_authenticate(user=self.user)

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

    def test_paginates_curriculum_plans(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'{self.endpoint}?page=2&page_size=1')

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
