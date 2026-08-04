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


class PlatformAdminCurriculumPlanWriteTests(
    APITestCase,
):
    list_endpoint = '/api/v1/admin/curriculum-plans/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.plan.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='student.plan.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.systems = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )
        self.industrial = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Industrial',
        )
        self.plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2025',
            name='Plan de Estudios 2025',
        )
        self.detail_endpoint = f'{self.list_endpoint}{self.plan.public_id}/'

    def test_rejects_unauthenticated_create(self) -> None:
        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': str(self.systems.public_id),
                'code': '2026',
                'name': 'Plan de Estudios 2026',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_student_create(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': str(self.systems.public_id),
                'code': '2026',
                'name': 'Plan de Estudios 2026',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creates_normalized_plan(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': str(self.systems.public_id),
                'code': '  plan   2026 ',
                'name': '  Plan   de   Estudios   2026 ',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['code'],
            'PLAN 2026',
        )
        self.assertEqual(
            response.json()['data']['name'],
            'Plan de Estudios 2026',
        )

    def test_rejects_unknown_school_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': ('11111111-1111-4111-8111-111111111111'),
                'code': '2026',
                'name': 'Plan de Estudios 2026',
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

    def test_rejects_duplicate_code_in_same_school(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': str(self.systems.public_id),
                'code': ' 2025 ',
                'name': 'Plan duplicado',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'code',
            response.json()['error']['errors'],
        )

    def test_allows_same_code_in_other_school(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'professional_school_id': str(self.industrial.public_id),
                'code': '2025',
                'name': 'Plan Industrial 2025',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_updates_plan_fields(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'code': 'PLAN 2025-A',
                'name': 'Plan Actualizado',
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.plan.refresh_from_db()

        self.assertEqual(self.plan.code, 'PLAN 2025-A')
        self.assertEqual(self.plan.name, 'Plan Actualizado')
        self.assertFalse(self.plan.is_active)

    def test_rejects_changing_school(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'professional_school_id': str(self.industrial.public_id),
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

    def test_rejects_duplicate_code_on_update(self) -> None:
        other_plan = CurriculumPlan.objects.create(
            professional_school=self.systems,
            code='2026',
            name='Plan de Estudios 2026',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            (f'{self.list_endpoint}{other_plan.public_id}/'),
            {
                'code': '2025',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'code',
            response.json()['error']['errors'],
        )

    def test_rejects_student_update(self) -> None:
        self.client.force_authenticate(user=self.student)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_returns_not_found_for_unknown_plan(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            (f'{self.list_endpoint}11111111-1111-4111-8111-111111111111/'),
            {
                'is_active': False,
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
            self.detail_endpoint,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'non_field_errors',
            response.json()['error']['errors'],
        )

    def test_rejects_delete(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            self.detail_endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertTrue(
            CurriculumPlan.objects.filter(
                pk=self.plan.pk,
            ).exists()
        )
