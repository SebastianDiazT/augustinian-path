from uuid import UUID

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import Faculty


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
