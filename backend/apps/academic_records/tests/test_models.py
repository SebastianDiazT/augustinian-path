from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db


def test_enrollment_str_and_school(course_enrollment_factory):
    enrollment = course_enrollment_factory()
    assert str(enrollment.student) in str(enrollment)
    assert str(enrollment.offering) in str(enrollment)
    assert enrollment.get_school() == enrollment.offering.course.curriculum_plan.school


def test_grade_str(grade_factory):
    grade = grade_factory(score=Decimal('14.50'))
    assert '14.50' in str(grade)
    assert str(grade.evaluation_component.name) in str(grade)


def test_compute_weighted_average(
    course_enrollment_factory, evaluation_component_factory, grade_factory
):
    enrollment = course_enrollment_factory()

    comp1 = evaluation_component_factory(weight=Decimal('40.0'))
    comp2 = evaluation_component_factory(weight=Decimal('60.0'))

    grade_factory(enrollment=enrollment, evaluation_component=comp1, score=Decimal('15.0'))
    grade_factory(enrollment=enrollment, evaluation_component=comp2, score=Decimal('10.0'))

    assert enrollment.compute_weighted_average() == Decimal('12.0')
