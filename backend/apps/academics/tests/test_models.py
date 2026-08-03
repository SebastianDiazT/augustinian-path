from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from apps.academics.models import Faculty, ProfessionalSchool


class FacultyTests(TestCase):
    def test_creates_active_faculty_with_public_id(self) -> None:
        faculty = Faculty.objects.create(
            name='Facultad de Ciencias Naturales y Formales',
        )

        self.assertIsInstance(faculty.public_id, UUID)
        self.assertTrue(faculty.is_active)
        self.assertIsNotNone(faculty.created_at)
        self.assertIsNotNone(faculty.updated_at)

    def test_normalizes_name_whitespace(self) -> None:
        faculty = Faculty.objects.create(
            name='  Facultad   de   Ingeniería  ',
        )

        self.assertEqual(
            faculty.name,
            'Facultad de Ingeniería',
        )

    def test_rejects_case_insensitive_duplicate_name(
        self,
    ) -> None:
        Faculty.objects.create(
            name='Facultad de Medicina',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Faculty.objects.create(
                    name='FACULTAD DE MEDICINA',
                )

    def test_rejects_empty_normalized_name(self) -> None:
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Faculty.objects.create(name='   ')

    def test_orders_faculties_by_name(self) -> None:
        Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        Faculty.objects.create(
            name='Facultad de Ciencias',
        )

        self.assertEqual(
            list(
                Faculty.objects.values_list(
                    'name',
                    flat=True,
                )
            ),
            [
                'Facultad de Ciencias',
                'Facultad de Ingenieria',
            ],
        )


class ProfessionalSchoolTests(TestCase):
    def setUp(self) -> None:
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )

    def test_creates_school_related_to_faculty(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertIsInstance(school.public_id, UUID)
        self.assertTrue(school.is_active)
        self.assertEqual(school.faculty, self.faculty)
        self.assertIn(
            school,
            self.faculty.professional_schools.all(),
        )

    def test_normalizes_name_whitespace(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='  Escuela   Profesional   de Sistemas  ',
        )

        self.assertEqual(
            school.name,
            'Escuela Profesional de Sistemas',
        )

    def test_rejects_duplicate_name_in_same_faculty(
        self,
    ) -> None:
        ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProfessionalSchool.objects.create(
                    faculty=self.faculty,
                    name='ESCUELA PROFESIONAL DE SISTEMAS',
                )

    def test_allows_same_name_in_different_faculty(
        self,
    ) -> None:
        other_faculty = Faculty.objects.create(
            name='Facultad de Ciencias',
        )

        first_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )
        second_school = ProfessionalSchool.objects.create(
            faculty=other_faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertNotEqual(
            first_school.public_id,
            second_school.public_id,
        )

    def test_protects_faculty_with_related_schools(
        self,
    ) -> None:
        ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        with self.assertRaises(ProtectedError):
            self.faculty.delete()

    def test_returns_descriptive_string(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertEqual(
            str(school),
            ('Escuela Profesional de Sistemas (Facultad de Ingenieria)'),
        )
