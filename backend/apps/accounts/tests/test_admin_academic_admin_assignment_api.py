from uuid import uuid4

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty, ProfessionalSchool
from apps.accounts.models import (
    AcademicAdminAssignment,
    User,
)
from apps.accounts.roles import Role


class PlatformAdminAcademicAdminAssignmentEndpointTests(
    APITestCase,
):
    def setUp(self) -> None:
        self.platform_admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        self.academic_admin_group = Group.objects.get(
            name=Role.ACADEMIC_ADMIN.value,
        )
        self.student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.platform_admin = User.objects.create_user(
            email='admin.asignaciones@unsa.edu.pe',
            password='Prueba123!',
        )
        self.platform_admin.groups.add(
            self.platform_admin_group,
        )

        self.student = User.objects.create_user(
            email='usuario.asignado@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            self.student_group,
        )

        self.faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Ingeniería de Sistemas',
        )
        self.another_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Ingeniería de Software',
        )

        self.endpoint = (
            f'/api/v1/admin/users/{self.student.public_id}/academic-admin-assignment/'
        )

    def test_rejects_unauthenticated_request(self) -> None:
        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_student_user(self) -> None:
        self.client.force_authenticate(
            user=self.student,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rejects_academic_admin_user(self) -> None:
        academic_admin = User.objects.create_user(
            email='admin.limitado@unsa.edu.pe',
            password='Prueba123!',
        )
        academic_admin.groups.add(
            self.academic_admin_group,
        )
        AcademicAdminAssignment.objects.create(
            user=academic_admin,
            professional_school=self.school,
        )

        self.client.force_authenticate(
            user=academic_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.another_school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_assigns_academic_admin_role_and_school(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        assignment = AcademicAdminAssignment.objects.get(
            user=self.student,
        )

        self.assertEqual(
            assignment.professional_school,
            self.school,
        )
        self.assertTrue(
            self.student.groups.filter(
                name=Role.ACADEMIC_ADMIN.value,
            ).exists()
        )
        self.assertEqual(
            response.json()['data']['roles'],
            [
                'academic_admin',
                'student',
            ],
        )
        self.assertEqual(
            response.json()['data']['academic_admin_school'],
            {
                'id': str(self.school.public_id),
                'name': self.school.name,
            },
        )

    def test_changes_existing_school_assignment(self) -> None:
        AcademicAdminAssignment.objects.create(
            user=self.student,
            professional_school=self.school,
        )
        self.student.groups.add(
            self.academic_admin_group,
        )
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.another_school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            AcademicAdminAssignment.objects.filter(
                user=self.student,
            ).count(),
            1,
        )
        self.assertEqual(
            AcademicAdminAssignment.objects.get(
                user=self.student,
            ).professional_school,
            self.another_school,
        )

    def test_rejects_inactive_school(self) -> None:
        self.school.is_active = False
        self.school.save(
            update_fields=['is_active'],
        )
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertFalse(
            AcademicAdminAssignment.objects.filter(
                user=self.student,
            ).exists()
        )

    def test_rejects_unknown_school(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(uuid4()),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_rejects_inactive_target_user(self) -> None:
        self.student.is_active = False
        self.student.save(
            update_fields=['is_active'],
        )
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.put(
            self.endpoint,
            {
                'professional_school_id': str(
                    self.school.public_id,
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'user_id',
            response.json()['error']['errors'],
        )

    def test_removes_assignment_and_academic_admin_role(self) -> None:
        AcademicAdminAssignment.objects.create(
            user=self.student,
            professional_school=self.school,
        )
        self.student.groups.add(
            self.academic_admin_group,
        )
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        response = self.client.delete(
            self.endpoint,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertFalse(
            AcademicAdminAssignment.objects.filter(
                user=self.student,
            ).exists()
        )
        self.assertFalse(
            self.student.groups.filter(
                name=Role.ACADEMIC_ADMIN.value,
            ).exists()
        )
        self.assertTrue(
            self.student.groups.filter(
                name=Role.STUDENT.value,
            ).exists()
        )
        self.assertEqual(
            response.json()['data']['roles'],
            [
                'student',
            ],
        )
        self.assertIsNone(
            response.json()['data']['academic_admin_school'],
        )

    def test_removal_is_idempotent(self) -> None:
        self.client.force_authenticate(
            user=self.platform_admin,
        )

        first_response = self.client.delete(
            self.endpoint,
        )
        second_response = self.client.delete(
            self.endpoint,
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )
