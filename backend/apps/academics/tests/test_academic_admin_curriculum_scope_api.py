from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import (
    AcademicAdminAssignment,
    User,
)
from apps.accounts.roles import Role


class AcademicAdminCurriculumPlanScopeTests(
    APITestCase,
):
    endpoint = '/api/v1/admin/curriculum-plans/'

    def setUp(self) -> None:
        academic_admin_group = Group.objects.get(
            name=Role.ACADEMIC_ADMIN.value,
        )

        self.academic_admin = User.objects.create_user(
            email='admin.sistemas@unsa.edu.pe',
            password='Prueba123!',
        )
        self.academic_admin.groups.add(
            academic_admin_group,
        )

        self.unassigned_admin = User.objects.create_user(
            email='admin.sin.escuela@unsa.edu.pe',
            password='Prueba123!',
        )
        self.unassigned_admin.groups.add(
            academic_admin_group,
        )

        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        self.industrial = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería Industrial',
        )

        AcademicAdminAssignment.objects.create(
            user=self.academic_admin,
            professional_school=self.systems,
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

    def detail_endpoint(
        self,
        plan: CurriculumPlan,
    ) -> str:
        return f'{self.endpoint}{plan.public_id}/'

    def test_rejects_academic_admin_without_assignment(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.unassigned_admin,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_lists_only_assigned_school_plans(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [plan['id'] for plan in response.json()['data']['curriculum_plans']],
            [
                str(self.systems_plan.public_id),
            ],
        )

    def test_filtering_another_school_returns_empty_list(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.get(
            f'{self.endpoint}?professional_school={self.industrial.public_id}'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.json()['data']['curriculum_plans'],
            [],
        )

    def test_creates_plan_in_assigned_school(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.systems.public_id,
                ),
                'code': '2026',
                'name': 'Plan Sistemas 2026',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            CurriculumPlan.objects.filter(
                professional_school=self.systems,
                code='2026',
            ).exists()
        )

    def test_rejects_create_in_another_school(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.industrial.public_id,
                ),
                'code': '2026',
                'name': 'Plan Industrial 2026',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'professional_school_id',
            response.json()['error']['errors'],
        )

    def test_updates_plan_from_assigned_school(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.patch(
            self.detail_endpoint(
                self.systems_plan,
            ),
            {
                'name': 'Plan de Sistemas actualizado',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.systems_plan.refresh_from_db()

        self.assertEqual(
            self.systems_plan.name,
            'Plan de Sistemas actualizado',
        )

    def test_hides_plan_from_another_school(self) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.patch(
            self.detail_endpoint(
                self.industrial_plan,
            ),
            {
                'name': 'Cambio no permitido',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.industrial_plan.refresh_from_db()

        self.assertEqual(
            self.industrial_plan.name,
            'Plan Industrial 2024',
        )
