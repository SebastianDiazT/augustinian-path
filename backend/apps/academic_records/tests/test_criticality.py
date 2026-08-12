from decimal import Decimal

import pytest

from apps.academic_records.criticality import compute_criticality_score, pick_course_to_drop
from apps.curricula.models import Prerequisite

pytestmark = pytest.mark.django_db


def test_compute_criticality_blocks_courses(
    student_profile_factory, curriculum_plan_factory, course_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course_root = course_factory(curriculum_plan=plan)
    course_child1 = course_factory(curriculum_plan=plan)
    course_child2 = course_factory(curriculum_plan=plan)

    Prerequisite.objects.create(course=course_child1, required_course=course_root)
    Prerequisite.objects.create(course=course_child2, required_course=course_root)

    course_isolated = course_factory(curriculum_plan=plan)

    score_root = compute_criticality_score(student, course_root)
    score_isolated = compute_criticality_score(student, course_isolated)

    assert score_root > score_isolated


def test_pick_course_to_drop(student_profile_factory, curriculum_plan_factory, course_factory):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course_a = course_factory(curriculum_plan=plan)
    course_b = course_factory(curriculum_plan=plan)
    Prerequisite.objects.create(course=course_b, required_course=course_a)

    course_c = course_factory(curriculum_plan=plan)

    kept, dropped, reason = pick_course_to_drop(student, course_a, course_c)

    assert kept == course_a
    assert dropped == course_c
    assert 'se priorizó' in reason
    assert course_a.name in reason


def test_pick_course_to_drop_equal_and_b_greater(
    student_profile_factory, curriculum_plan_factory, course_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course_a = course_factory(curriculum_plan=plan)
    course_b = course_factory(curriculum_plan=plan)

    assert pick_course_to_drop(student, course_a, course_b) is None

    Prerequisite.objects.create(course=course_a, required_course=course_b)
    kept, dropped, _ = pick_course_to_drop(student, course_a, course_b)
    assert kept == course_b


def test_criticality_elective_branch(
    student_profile_factory, curriculum_plan_factory, course_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course = course_factory(curriculum_plan=plan, course_type='elective')
    course.branch_id = 99

    score = compute_criticality_score(student, course)
    assert score > Decimal('0')