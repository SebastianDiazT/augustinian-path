from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth import get_user_model

from .models import CurriculumCourse, StudentCourseAttempt

User = get_user_model()


@dataclass(frozen=True)
class CourseEligibility:
    available: bool
    approved_credits: Decimal
    required_credits: Decimal
    missing_prerequisites: tuple[CurriculumCourse, ...]

    @property
    def credits_met(self) -> bool:
        return self.approved_credits >= self.required_credits

    def blocking_message(self) -> str:
        reasons = []

        if self.missing_prerequisites:
            course_codes = ', '.join(
                prerequisite.course.code
                for prerequisite in self.missing_prerequisites
            )
            reasons.append(f'falta aprobar: {course_codes}')

        if not self.credits_met:
            reasons.append(
                'requiere '
                f'{self.required_credits:.2f} créditos aprobados y tiene '
                f'{self.approved_credits:.2f}'
            )

        return '; '.join(reasons)

    def as_dict(self) -> dict[str, object]:
        return {
            'available': self.available,
            'approved_credits': f'{self.approved_credits:.2f}',
            'required_credits': f'{self.required_credits:.2f}',
            'credits_met': self.credits_met,
            'missing_prerequisites': [
                {
                    'curriculum_course_id': str(prerequisite.public_id),
                    'course_code': prerequisite.course.code,
                    'course_name': prerequisite.course.name,
                }
                for prerequisite in self.missing_prerequisites
            ],
        }


@dataclass(frozen=True)
class StudentAcademicProgress:
    passed_curriculum_course_ids: frozenset[int]
    approved_credits: Decimal


def get_student_academic_progress(
    student: User,
    curriculum_course: CurriculumCourse,
) -> StudentAcademicProgress:
    passed_attempts = (
        StudentCourseAttempt.objects.filter(
            student=student,
            status=StudentCourseAttempt.Status.PASSED,
            curriculum_course__curriculum_plan=(
                curriculum_course.curriculum_plan
            ),
        )
        .select_related(
            'curriculum_course',
            'curriculum_course__course',
        )
        .order_by('pk')
    )
    passed_curriculum_courses = {
        attempt.curriculum_course_id: attempt.curriculum_course
        for attempt in passed_attempts
    }
    return StudentAcademicProgress(
        passed_curriculum_course_ids=frozenset(
            passed_curriculum_courses,
        ),
        approved_credits=sum(
            (
                passed_curriculum_course.credits
                for passed_curriculum_course in passed_curriculum_courses.values()
            ),
            start=Decimal('0.00'),
        ),
    )


def evaluate_course_eligibility(
    student: User,
    curriculum_course: CurriculumCourse,
    *,
    progress: StudentAcademicProgress | None = None,
) -> CourseEligibility:
    if progress is None:
        progress = get_student_academic_progress(
            student,
            curriculum_course,
        )

    prerequisites = tuple(
        curriculum_course.prerequisites.select_related('course').all()
    )
    missing_prerequisites = tuple(
        prerequisite
        for prerequisite in prerequisites
        if prerequisite.pk not in progress.passed_curriculum_course_ids
    )
    required_credits = curriculum_course.prerequisite_credits

    return CourseEligibility(
        available=(
            not missing_prerequisites
            and progress.approved_credits >= required_credits
        ),
        approved_credits=progress.approved_credits,
        required_credits=required_credits,
        missing_prerequisites=missing_prerequisites,
    )
