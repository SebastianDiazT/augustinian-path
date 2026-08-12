from decimal import Decimal

import pytest

from apps.academic_records.models import CourseEnrollment
from apps.academic_records.progress import compute_eligible_courses, compute_progress
from apps.curricula.models import Prerequisite

pytestmark = pytest.mark.django_db


def test_compute_progress(
    student_profile_factory, curriculum_plan_factory, course_factory, course_enrollment_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course1 = course_factory(curriculum_plan=plan, credits=Decimal('10.0'))
    course_enrollment_factory(
        student=student, offering__course=course1, status=CourseEnrollment.Status.PASSED
    )

    course2 = course_factory(curriculum_plan=plan, credits=Decimal('5.0'))
    course_enrollment_factory(
        student=student, offering__course=course2, status=CourseEnrollment.Status.IN_PROGRESS
    )

    progress = compute_progress(student, plan)

    assert progress['courses_passed'] == 1
    assert progress['courses_in_progress'] == 1
    assert progress['credits_completed'] == Decimal('10.0')


def test_compute_eligible_courses(
    student_profile_factory, curriculum_plan_factory, course_factory, course_enrollment_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course_a = course_factory(curriculum_plan=plan)
    course_b = course_factory(curriculum_plan=plan)

    Prerequisite.objects.create(course=course_b, required_course=course_a)

    entries = compute_eligible_courses(student, plan)

    entry_b = next(e for e in entries if e['course'].id == course_b.id)
    assert entry_b['is_eligible'] is False
    assert course_a in entry_b['missing_prerequisites']

    course_enrollment_factory(
        student=student, offering__course=course_a, status=CourseEnrollment.Status.PASSED
    )

    entries_after = compute_eligible_courses(student, plan)
    entry_b_after = next(e for e in entries_after if e['course'].id == course_b.id)
    assert entry_b_after['is_eligible'] is True


def test_compute_eligible_courses_missing_credits(
    student_profile_factory, curriculum_plan_factory, course_factory
):
    student = student_profile_factory()
    plan = curriculum_plan_factory()

    course = course_factory(curriculum_plan=plan)
    course.min_credits_required = Decimal('100.0')
    course.save()

    entries = compute_eligible_courses(student, plan)
    entry = next(e for e in entries if e['course'].id == course.id)

    assert entry['is_eligible'] is False
    assert entry['missing_credits'] == Decimal('100.0')