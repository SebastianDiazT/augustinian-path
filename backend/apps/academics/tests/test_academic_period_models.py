from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    CurriculumCourse,
    CurriculumPlan,
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
        self.curriculum_plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2017',
            name='Plan de Estudios 2017',
        )
        self.programming_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.curriculum_plan,
            course=self.programming,
            cycle=1,
            credits=Decimal('5.00'),
        )
        self.databases_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.curriculum_plan,
            course=self.databases,
            cycle=5,
            credits=Decimal('4.00'),
        )
        self.first_period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        self.second_period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
        )

    def test_represents_course_and_period(self) -> None:
        offering = CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
        )
        offering.curriculum_courses.add(
            self.programming_entry,
        )

        self.assertEqual(
            list(offering.curriculum_courses.all()),
            [self.programming_entry],
        )
        self.assertEqual(
            str(offering),
            '2026-A: CS 101',
        )

    def test_links_same_course_from_multiple_curriculum_versions(
        self,
    ) -> None:
        other_plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2025',
            name='Plan de Estudios 2025',
        )
        other_entry = CurriculumCourse.objects.create(
            curriculum_plan=other_plan,
            course=self.programming,
            cycle=2,
            credits=Decimal('4.00'),
        )
        offering = CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
        )
        offering.curriculum_courses.set(
            [
                self.programming_entry,
                other_entry,
            ]
        )

        self.assertEqual(
            offering.curriculum_courses.count(),
            2,
        )

    def test_rejects_duplicate_course_in_period(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseOffering.objects.create(
                    academic_period=self.first_period,
                    course=self.programming,
                )

    def test_allows_different_courses_in_same_period(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
        )
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.databases,
        )

        self.assertEqual(
            CourseOffering.objects.filter(
                academic_period=self.first_period,
            ).count(),
            2,
        )

    def test_allows_same_course_in_different_periods(
        self,
    ) -> None:
        CourseOffering.objects.create(
            academic_period=self.first_period,
            course=self.programming,
        )
        CourseOffering.objects.create(
            academic_period=self.second_period,
            course=self.programming,
        )

        self.assertEqual(
            CourseOffering.objects.filter(
                course=self.programming,
            ).count(),
            2,
        )
