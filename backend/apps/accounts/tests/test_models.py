from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import Faculty, ProfessionalSchool
from apps.accounts.models import AcademicAdminAssignment

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self) -> None:
        user = User.objects.create_user(
            email='USUARIO.PRUEBA@UNSA.EDU.PE',
            password='Prueba123!',
        )

        self.assertEqual(user.email, 'usuario.prueba@unsa.edu.pe')
        self.assertTrue(user.check_password('Prueba123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_rejects_non_institutional_email(self) -> None:
        with self.assertRaises(ValidationError):
            User.objects.create_user(
                email='persona@gmail.com',
                password='Prueba123!',
            )

        self.assertFalse(User.objects.filter(email='persona@gmail.com').exists())

    def test_create_superuser_assigns_permissions(self) -> None:
        user = User.objects.create_superuser(
            email='admin@unsa.edu.pe',
            password='Prueba123!',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_generates_public_id(self) -> None:
        user = User.objects.create_user(
            email='public.id@unsa.edu.pe',
            password='Prueba123!',
        )

        self.assertIsInstance(user.public_id, UUID)


class AcademicAdminAssignmentTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='administrador.escuela@unsa.edu.pe',
            password='Prueba123!',
        )
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Ingeniería de Sistemas',
        )

    def test_creates_assignment_with_public_id(self) -> None:
        assignment = AcademicAdminAssignment.objects.create(
            user=self.user,
            professional_school=self.school,
        )

        self.assertIsInstance(
            assignment.public_id,
            UUID,
        )
        self.assertEqual(
            assignment.professional_school,
            self.school,
        )
        self.assertEqual(
            str(assignment),
            ('administrador.escuela@unsa.edu.pe — Ingeniería de Sistemas'),
        )

    def test_user_can_only_have_one_school_assignment(self) -> None:
        AcademicAdminAssignment.objects.create(
            user=self.user,
            professional_school=self.school,
        )
        another_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Ingeniería de Software',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AcademicAdminAssignment.objects.create(
                    user=self.user,
                    professional_school=another_school,
                )
