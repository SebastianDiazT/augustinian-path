from uuid import uuid4

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    AcademicPeriod,
    Faculty,
    ProfessionalSchool,
)
from apps.accounts.models import (
    AcademicAdminAssignment,
    User,
)
from apps.accounts.roles import Role


class AcademicPeriodAdminEndpointTests(APITestCase):
    endpoint = '/api/v1/admin/academic-periods/'

    def setUp(self) -> None:
        platform_admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        academic_admin_group = Group.objects.get(
            name=Role.ACADEMIC_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.platform_admin = User.objects.create_user(
            email='platform.periods@unsa.edu.pe',
            password='Prueba123!',
        )
        self.platform_admin.groups.add(
            platform_admin_group,
        )

        self.academic_admin = User.objects.create_user(
            email='academic.periods@unsa.edu.pe',
            password='Prueba123!',
        )
        self.academic_admin.groups.add(
            academic_admin_group,
        )

        self.unassigned_admin = User.objects.create_user(
            email='unassigned.periods@unsa.edu.pe',
            password='Prueba123!',
        )
        self.unassigned_admin.groups.add(
            academic_admin_group,
        )

        self.student = User.objects.create_user(
            email='student.periods@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            student_group,
        )

        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )

        AcademicAdminAssignment.objects.create(
            user=self.academic_admin,
            professional_school=school,
        )

        self.period_a = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        self.period_b = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
            is_active=False,
        )

    def detail_endpoint(
        self,
        period: AcademicPeriod,
    ) -> str:
        return f'{self.endpoint}{period.public_id}/'

    def test_rejects_unauthenticated_list(self) -> None:
        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_rejects_student_list(self) -> None:
        self.client.force_authenticate(
            user=self.student,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_allows_platform_admin_list(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.get(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {period['code'] for period in response.json()['data']['academic_periods']},
            {
                '2026-A',
                '2026-B',
            },
        )

    def test_allows_assigned_academic_admin_list(
        self,
    ) -> None:
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

    def test_rejects_unassigned_academic_admin_list(
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

    def test_filters_periods(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.get(f'{self.endpoint}?year=2026&term=A&is_active=true')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            [period['id'] for period in response.json()['data']['academic_periods']],
            [
                str(self.period_a.public_id),
            ],
        )

    def test_rejects_invalid_term_filter(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.get(
            f'{self.endpoint}?term=C',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_platform_admin_creates_period(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'year': 2027,
                'term': AcademicPeriod.Term.FIRST,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['code'],
            '2027-A',
        )
        self.assertTrue(
            AcademicPeriod.objects.filter(
                year=2027,
                term=AcademicPeriod.Term.FIRST,
            ).exists()
        )

    def test_academic_admin_cannot_create_period(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'year': 2027,
                'term': AcademicPeriod.Term.FIRST,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_duplicate_period(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'year': 2026,
                'term': AcademicPeriod.Term.FIRST,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'term',
            response.json()['error']['errors'],
        )

    def test_rejects_unknown_term(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.post(
            self.endpoint,
            {
                'year': 2027,
                'term': 'C',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'term',
            response.json()['error']['errors'],
        )

    def test_platform_admin_updates_period_status(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.patch(
            self.detail_endpoint(
                self.period_a,
            ),
            {
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.period_a.refresh_from_db()

        self.assertFalse(
            self.period_a.is_active,
        )

    def test_academic_admin_cannot_update_period(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.academic_admin,
        )

        response = self.client.patch(
            self.detail_endpoint(
                self.period_a,
            ),
            {
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_changing_period_identity(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.patch(
            self.detail_endpoint(
                self.period_a,
            ),
            {
                'year': 2027,
                'term': AcademicPeriod.Term.SECOND,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'year',
            response.json()['error']['errors'],
        )
        self.assertIn(
            'term',
            response.json()['error']['errors'],
        )

    def test_returns_not_found_for_unknown_period(
        self,
    ) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.patch(
            f'{self.endpoint}{uuid4()}/',
            {
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
