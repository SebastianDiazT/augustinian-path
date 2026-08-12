from decimal import Decimal

from django.db.models import Sum

from apps.curricula.models import Course, Prerequisite

from .models import CourseEnrollment

WEIGHT_BLOCKS_COURSES = Decimal('10')
WEIGHT_CREDIT_GATE = Decimal('1')
WEIGHT_ELECTIVE_BRANCH = Decimal('5')


def passed_course_ids(student):
    return set(
        CourseEnrollment.objects.filter(
            student=student, status=CourseEnrollment.Status.PASSED,
        ).values_list('offering__course_id', flat=True),
    )


def build_prerequisite_graph(curriculum_plan):
    graph = {}
    rows = Prerequisite.objects.filter(
        course__curriculum_plan=curriculum_plan,
    ).values('course_id', 'required_course_id')
    for row in rows:
        graph.setdefault(row['required_course_id'], set()).add(row['course_id'])
    return graph


def _transitively_blocked_course_ids(course, graph):
    visited = set()
    frontier = {course.id}
    while frontier:
        next_frontier = set()
        for course_id in frontier:
            for dependent_id in graph.get(course_id, ()):
                if dependent_id not in visited:
                    visited.add(dependent_id)
                    next_frontier.add(dependent_id)
        frontier = next_frontier
    return visited


def accumulated_credits(plan, passed_ids):
    total = Course.objects.filter(
        id__in=passed_ids, curriculum_plan=plan,
    ).aggregate(total=Sum('credits'))['total']
    return total or Decimal('0')


def started_elective_branch_ids(plan, passed_ids):
    return set(
        Course.objects.filter(
            id__in=passed_ids, curriculum_plan=plan, branch__isnull=False,
        ).values_list('branch_id', flat=True),
    )


def compute_criticality_score(student, course, *, known_passed_ids=None, prereq_graph=None):
    passed_ids = known_passed_ids if known_passed_ids is not None else passed_course_ids(student)
    graph = (
        prereq_graph
        if prereq_graph is not None
        else build_prerequisite_graph(course.curriculum_plan)
    )

    blocked_ids = _transitively_blocked_course_ids(course, graph)
    signal_1 = len(blocked_ids - passed_ids)

    plan = course.curriculum_plan
    completed_credits = accumulated_credits(plan, passed_ids)
    still_credit_gated = plan.courses.filter(
        min_credits_required__isnull=False,
        min_credits_required__gt=completed_credits,
    ).exclude(id__in=passed_ids).exists()
    signal_2 = course.credits if still_credit_gated else Decimal('0')

    signal_3 = Decimal('0')
    if course.branch_id and course.course_type == Course.CourseType.ELECTIVE:
        started_branches = started_elective_branch_ids(plan, passed_ids)
        needs_more_branches = len(started_branches) < plan.min_elective_branches_to_complete
        if needs_more_branches and course.branch_id not in started_branches:
            signal_3 = Decimal('1')

    return (
        Decimal(signal_1) * WEIGHT_BLOCKS_COURSES
        + signal_2 * WEIGHT_CREDIT_GATE
        + signal_3 * WEIGHT_ELECTIVE_BRANCH
    )


def pick_course_to_drop(student, course_a, course_b):
    passed_ids = passed_course_ids(student)
    graph_a = build_prerequisite_graph(course_a.curriculum_plan)
    graph_b = (
        graph_a if course_b.curriculum_plan_id == course_a.curriculum_plan_id
        else build_prerequisite_graph(course_b.curriculum_plan)
    )

    score_a = compute_criticality_score(
        student,
        course_a,
        known_passed_ids=passed_ids,
        prereq_graph=graph_a,
    )
    score_b = compute_criticality_score(
        student,
        course_b,
        known_passed_ids=passed_ids,
        prereq_graph=graph_b,
    )

    if score_a == score_b:
        return None
    kept, dropped = (course_a, course_b) if score_a > score_b else (course_b, course_a)
    reason = (
        f'Se excluyó "{dropped.name}" porque se cruza por completo con '
        f'"{kept.name}" y no hay forma de llevarlos juntos en el mismo '
        f'horario; se priorizó "{kept.name}" por ser más crítico para tu '
        'avance académico.'
    )
    return kept, dropped, reason
