from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    Faculty,
    ProfessionalSchool,
)
from apps.grading.models import EvaluationComponent, EvaluationScheme
from apps.grading.services import GradeSimulationError, simulate_grades


class GradingModelAndServiceTests(TestCase):
    def setUp(self) -> None:
        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        course = Course.objects.create(
            professional_school=school,
            code='CS 101',
            name='Programación',
        )
        period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
        )
        offering = CourseOffering.objects.create(
            academic_period=period,
            course=course,
        )
        self.scheme = EvaluationScheme.objects.create(
            course_offering=offering,
        )
        self.exam_1 = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Examen 1',
            component_type=EvaluationComponent.ComponentType.EXAM_1,
            weight=Decimal('30.00'),
            order=1,
        )
        self.exam_2 = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Examen 2',
            component_type=EvaluationComponent.ComponentType.EXAM_2,
            weight=Decimal('30.00'),
            order=2,
        )
        self.continuous = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Evaluación continua',
            component_type=EvaluationComponent.ComponentType.OTHER,
            weight=Decimal('40.00'),
            order=3,
        )
        self.substitute = EvaluationComponent.objects.create(
            scheme=self.scheme,
            name='Sustitutorio',
            component_type=EvaluationComponent.ComponentType.SUBSTITUTE,
            weight=Decimal('0.00'),
            order=4,
        )

    def test_enforces_exact_passing_grade(self) -> None:
        self.scheme.passing_grade = Decimal('10.49')

        with self.assertRaises(ValidationError):
            self.scheme.save()

    def test_rejects_weight_for_substitute(self) -> None:
        component = EvaluationComponent(
            scheme=self.scheme,
            name='Otro sustitutorio',
            component_type=EvaluationComponent.ComponentType.SUBSTITUTE,
            weight=Decimal('10.00'),
        )

        with self.assertRaises(ValidationError) as context:
            component.full_clean()

        self.assertIn('weight', context.exception.message_dict)

    def test_passes_at_exactly_ten_point_fifty(self) -> None:
        result = simulate_grades(
            self.scheme,
            {
                self.exam_1.pk: Decimal('10.50'),
                self.exam_2.pk: Decimal('10.50'),
                self.continuous.pk: Decimal('10.50'),
            },
        )

        self.assertEqual(result['final_average'], '10.50')
        self.assertTrue(result['passed'])
        self.assertEqual(result['points_missing'], '0.00')

    def test_substitute_replaces_lower_exam_even_when_score_is_lower(self) -> None:
        result = simulate_grades(
            self.scheme,
            {
                self.exam_1.pk: Decimal('12.00'),
                self.exam_2.pk: Decimal('16.00'),
                self.continuous.pk: Decimal('10.00'),
                self.substitute.pk: Decimal('5.00'),
            },
        )

        self.assertEqual(result['final_average'], '10.30')
        self.assertEqual(
            result['substitution']['replaced_component_id'],
            str(self.exam_1.public_id),
        )
        self.assertEqual(result['substitution']['original_score'], '12.00')
        self.assertEqual(result['substitution']['effective_score'], '5.00')

    def test_reports_minimum_for_each_pending_component(self) -> None:
        result = simulate_grades(
            self.scheme,
            {
                self.continuous.pk: Decimal('15.00'),
            },
        )

        self.assertEqual(result['final_average'], '6.00')
        self.assertEqual(result['points_missing'], '4.50')
        self.assertEqual(result['used_percentage'], '40.00')
        self.assertEqual(result['remaining_percentage'], '60.00')
        self.assertEqual(
            [item['minimum_score'] for item in result['pending_components']],
            [
                '15.00',
                '15.00',
            ],
        )

    def test_requires_both_exams_to_use_substitute(self) -> None:
        with self.assertRaises(GradeSimulationError):
            simulate_grades(
                self.scheme,
                {
                    self.exam_1.pk: Decimal('12.00'),
                    self.substitute.pk: Decimal('15.00'),
                },
            )

    def test_rejects_scheme_whose_weight_is_not_one_hundred(self) -> None:
        self.continuous.weight = Decimal('30.00')
        self.continuous.save()

        with self.assertRaises(GradeSimulationError):
            simulate_grades(
                self.scheme,
                {},
            )
