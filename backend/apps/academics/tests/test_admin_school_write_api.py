from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Faculty, ProfessionalSchool
from apps.accounts.models import User
from apps.accounts.roles import Role


class PlatformAdminSchoolWriteTests(APITestCase):
    list_endpoint = '/api/v1/admin/professional-schools/'

    def setUp(self) -> None:
        admin_group = Group.objects.get(
            name=Role.PLATFORM_ADMIN.value,
        )
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )

        self.admin = User.objects.create_user(
            email='admin.escuela.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin.groups.add(admin_group)

        self.student = User.objects.create_user(
            email='student.escuela.write@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)

        self.engineering = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.medicine = Faculty.objects.create(
            name='Facultad de Medicina',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.engineering,
            name='Escuela Profesional de Sistemas',
        )
        self.detail_endpoint = f'{self.list_endpoint}{self.school.public_id}/'

    def test_rejects_unauthenticated_create(self) -> None:
        response = self.client.post(
            self.list_endpoint,
            {
                'faculty_id': str(self.engineering.public_id),
                'name': 'Escuela Profesional de Industrial',
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
                'faculty_id': str(self.engineering.public_id),
                'name': 'Escuela Profesional de Industrial',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_creates_normalized_school(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'faculty_id': str(self.engineering.public_id),
                'name': ('  Escuela   Profesional   de Industrial  '),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['name'],
            'Escuela Profesional de Industrial',
        )
        self.assertEqual(
            response.json()['data']['faculty']['id'],
            str(self.engineering.public_id),
        )

    def test_rejects_unknown_faculty_uuid(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'faculty_id': ('11111111-1111-4111-8111-111111111111'),
                'name': 'Escuela Profesional de Industrial',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'faculty_id',
            response.json()['error']['errors'],
        )

    def test_rejects_duplicate_in_same_faculty(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'faculty_id': str(self.engineering.public_id),
                'name': (' ESCUELA   PROFESIONAL   DE SISTEMAS '),
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

    def test_allows_same_name_in_other_faculty(
        self,
    ) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_endpoint,
            {
                'faculty_id': str(self.medicine.public_id),
                'name': 'Escuela Profesional de Sistemas',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()['data']['faculty']['id'],
            str(self.medicine.public_id),
        )

    def test_updates_school_name_and_status(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'name': 'Escuela Profesional de Computacion',
                'is_active': False,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.school.refresh_from_db()

        self.assertEqual(
            self.school.name,
            'Escuela Profesional de Computacion',
        )
        self.assertFalse(self.school.is_active)

    def test_moves_school_to_another_faculty(self) -> None:
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'faculty_id': str(self.medicine.public_id),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.school.refresh_from_db()

        self.assertEqual(
            self.school.faculty,
            self.medicine,
        )

    def test_rejects_duplicate_when_moving_school(
        self,
    ) -> None:
        ProfessionalSchool.objects.create(
            faculty=self.medicine,
            name='Escuela Profesional de Sistemas',
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_endpoint,
            {
                'faculty_id': str(self.medicine.public_id),
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

    def test_returns_not_found_for_unknown_school(
        self,
    ) -> None:
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
            ProfessionalSchool.objects.filter(
                pk=self.school.pk,
            ).exists()
        )
