from decimal import Decimal

from apps.curricula.models import Course, Prerequisite

from .criticality import (
    accumulated_credits,
    passed_course_ids,
    started_elective_branch_ids,
)
from .models import CourseEnrollment


def compute_progress(student, curriculum_plan):
    passed_ids = passed_course_ids(student)
    credits_completed = accumulated_credits(curriculum_plan, passed_ids)

    passed_count = Course.objects.filter(
        id__in=passed_ids, curriculum_plan=curriculum_plan,
    ).count()
    total_courses = curriculum_plan.courses.filter(is_active=True).count()

    in_progress_count = CourseEnrollment.objects.filter(
        student=student,
        offering__course__curriculum_plan=curriculum_plan,
        status=CourseEnrollment.Status.IN_PROGRESS,
    ).count()

    started_branches = started_elective_branch_ids(curriculum_plan, passed_ids)

    total_required = curriculum_plan.total_credits_required
    percentage = None
    if total_required:
        percentage = min(Decimal('100'), (credits_completed / total_required) * Decimal('100'))

    return {
        'credits_completed': credits_completed,
        'credits_total_required': total_required,
        'progress_percentage': percentage,
        'courses_passed': passed_count,
        'courses_total_in_plan': total_courses,
        'courses_in_progress': in_progress_count,
        'elective_branches_completed': len(started_branches),
        'elective_branches_required': curriculum_plan.min_elective_branches_to_complete,
    }


def compute_eligible_courses(student, curriculum_plan):
    passed_ids = passed_course_ids(student)
    credits_completed = accumulated_credits(curriculum_plan, passed_ids)

    in_progress_ids = set(
        CourseEnrollment.objects.filter(
            student=student,
            offering__course__curriculum_plan=curriculum_plan,
            status=CourseEnrollment.Status.IN_PROGRESS,
        ).values_list('offering__course_id', flat=True),
    )

    prerequisites_by_course = {}
    rows = Prerequisite.objects.filter(
        course__curriculum_plan=curriculum_plan,
    ).select_related('required_course')
    for row in rows:
        prerequisites_by_course.setdefault(row.course_id, []).append(row.required_course)

    pending_courses = curriculum_plan.courses.filter(is_active=True).exclude(id__in=passed_ids)

    results = []
    for course in pending_courses:
        missing_prerequisites = [
            required for required in prerequisites_by_course.get(course.id, [])
            if required.id not in passed_ids
        ]
        missing_credits = None
        if course.min_credits_required and credits_completed < course.min_credits_required:
            missing_credits = course.min_credits_required - credits_completed

        results.append({
            'course': course,
            'is_eligible': not missing_prerequisites and missing_credits is None,
            'is_in_progress': course.id in in_progress_ids,
            'missing_prerequisites': missing_prerequisites,
            'missing_credits': missing_credits,
        })

    return results
