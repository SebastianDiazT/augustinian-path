from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminFacultyWriteTests(APITestCase):
    list_endpoint = '/api/v1/admin/faculties/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.escritura@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='estudiante.escritura@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.faculty = Faculty.objects.create(
            name='Facultad de Ciencias',
        )
        self.detail_endpoint = f'/api/v1/admin/faculties/{self.faculty.public_id}/'

    def test_rejects_unauthenticated_create(self) -> None:
        response = self.client.post(
            self.list_endpoint,
            {
                'name': 'Facultad de Medicina',
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
                'name': 'Facultad de Medicina',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creates_normalized_faculty(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'name': '  Facultad   de   Medicina  ',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['name'],
            'Facultad de Medicina',
        )
        self.assertTrue(response.json()['data']['is_active'])
        self.assertTrue(
            Faculty.objects.filter(
                public_id=response.json()['data']['id'],
                name='Facultad de Medicina',
            ).exists()
        )

    def test_rejects_duplicate_faculty_name(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'name': '  FACULTAD   DE   CIENCIAS ',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'name',
            response.json()['error']['errors'],
        )
        self.assertEqual(Faculty.objects.count(), 1)

    def test_updates_faculty_name_and_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'name': '  Facultad   de Ciencias Sociales ',
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.faculty.refresh_from_db()

        self.assertEqual(
            self.faculty.name,
            'Facultad de Ciencias Sociales',
        )
        self.assertFalse(self.faculty.is_active)

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

    def test_returns_not_found_for_unknown_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            ('/api/v1/admin/faculties/11111111-1111-4111-8111-111111111111/'),
            {
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertIn('error', response.json())

    def test_rejects_duplicate_name_on_update(self) -> None:
        other_faculty = Faculty.objects.create(
            name='Facultad de Medicina',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            (f'/api/v1/admin/faculties/{other_faculty.public_id}/'),
            {
                'name': 'FACULTAD DE CIENCIAS',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'name',
            response.json()['error']['errors'],
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
            Faculty.objects.filter(
                pk=self.faculty.pk,
            ).exists()
        )
