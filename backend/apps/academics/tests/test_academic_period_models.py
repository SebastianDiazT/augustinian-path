from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    Faculty,
    ProfessionalSchool,
)


class AcademicPeriodModelTests(TestCase):
    def test_builds_period_code(self) -> None:
        period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )

        self.assertEqual(
            period.code,
            '2026-A',
        )
        self.assertEqual(
            str(period),
            '2026-A',
        )

    def test_accepts_two_periods_in_same_year(self) -> None:
        first = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        second = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
        )

        self.assertEqual(first.code, '2026-A')
        self.assertEqual(second.code, '2026-B')

    def test_rejects_duplicate_period(self) -> None:
        AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AcademicPeriod.objects.create(
                    year=2026,
                    term=AcademicPeriod.Term.FIRST,
                )

    def test_rejects_unknown_term_during_validation(
        self,
    ) -> None:
        period = AcademicPeriod(
            year=2026,
            term='C',
        )

        with self.assertRaises(ValidationError):
            period.full_clean()


class CourseOfferingModelTests(TestCase):
    def setUp(self) -> None:
        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        self.programming = Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programación',
        )
        self.databases = Course.objects.create(
            professional_school=self.school,
            code='CS 201',
            name='Bases de Datos',
        )
        self.first_period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        self.second_period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
        )

    def test_normalizes_group_code(self) -> None:
        offering = CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='  a  ',
        )

        self.assertEqual(
            offering.group_code,
            'A',
        )
        self.assertEqual(
            str(offering),
            '2026-A: CS 101 — grupo A',
        )

    def test_allows_multiple_groups_for_same_course(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='A',
        )
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='B',
        )

        self.assertEqual(
            CourseOffering.objects.filter(
                academic_period=self.first_period,
                course=self.programming,
            ).count(),
            2,
        )

    def test_rejects_duplicate_group_case_insensitively(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='A',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseOffering.objects.create(
                    academic_period=self.first_period,
                    course=self.programming,
                    group_code='a',
                )

    def test_allows_same_group_for_different_courses(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='A',
        )
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.databases,
            group_code='A',
        )

        self.assertEqual(
            CourseOffering.objects.filter(
                academic_period=self.first_period,
                group_code='A',
            ).count(),
            2,
        )

    def test_allows_same_group_in_different_periods(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
            group_code='A',
        )
        CourseOffering.objects.create(
            academic_period=self.second_period,
            course=self.programming,
            group_code='A',
        )

        self.assertEqual(
            CourseOffering.objects.filter(
                course=self.programming,
                group_code='A',
            ).count(),
            2,
        )
