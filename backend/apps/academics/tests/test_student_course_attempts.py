from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.eligibility import evaluate_course_eligibility
from apps.academics.models import (
    AcademicPeriod,
    Course,
    CourseOffering,
    CurriculumCourse,
    CurriculumCoursePrerequisite,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
    StudentCourseAttempt,
)
from apps.accounts.models import User
from apps.accounts.roles import Role


class StudentCourseAttemptFixtureMixin:
    def build_fixture(self) -> None:
        faculty = Faculty.objects.create(name='Facultad de Ingeniería')
        self.school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        self.plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2017',
            name='Plan 2017',
        )
        self.previous_course = Course.objects.create(
            professional_school=self.school,
            code='CS101',
            name='Programación',
        )
        self.advanced_course = Course.objects.create(
            professional_school=self.school,
            code='CS201',
            name='Bases de Datos',
        )
        self.previous_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.previous_course,
            cycle=1,
            credits=Decimal('5.00'),
        )
        self.advanced_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.advanced_course,
            cycle=2,
            credits=Decimal('4.00'),
            prerequisite_credits=Decimal('5.00'),
        )
        CurriculumCoursePrerequisite.objects.create(
            curriculum_course=self.advanced_entry,
            prerequisite=self.previous_entry,
        )
        self.previous_period = AcademicPeriod.objects.create(
            year=2025,
            term=AcademicPeriod.Term.SECOND,
        )
        self.previous_offering = CourseOffering.objects.create(
            academic_period=self.previous_period,
            course=self.previous_course,
        )
        self.previous_offering.curriculum_courses.add(self.previous_entry)
        self.student = User.objects.create_user(
            email='history.student@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(
            Group.objects.get(name=Role.STUDENT.value),
        )


class StudentCourseAttemptModelTests(
    StudentCourseAttemptFixtureMixin,
    TestCase,
):
    def setUp(self) -> None:
        self.build_fixture()

    def test_requires_exact_passing_threshold_for_passed_status(self) -> None:
        with self.assertRaises(ValidationError) as context:
            StudentCourseAttempt.objects.create(
                student=self.student,
                course_offering=self.previous_offering,
                curriculum_course=self.previous_entry,
                status=StudentCourseAttempt.Status.PASSED,
                final_grade=Decimal('10.49'),
            )

        self.assertIn('final_grade', context.exception.message_dict)

    def test_unlocks_course_after_passing_subject_and_credit_requirements(
        self,
    ) -> None:
        blocked = evaluate_course_eligibility(
            self.student,
            self.advanced_entry,
        )

        self.assertFalse(blocked.available)
        self.assertEqual(
            blocked.missing_prerequisites,
            (self.previous_entry,),
        )
        self.assertEqual(blocked.approved_credits, Decimal('0.00'))

        StudentCourseAttempt.objects.create(
            student=self.student,
            course_offering=self.previous_offering,
            curriculum_course=self.previous_entry,
            status=StudentCourseAttempt.Status.PASSED,
            final_grade=Decimal('10.50'),
        )

        unlocked = evaluate_course_eligibility(
            self.student,
            self.advanced_entry,
        )

        self.assertTrue(unlocked.available)
        self.assertEqual(unlocked.missing_prerequisites, ())
        self.assertEqual(unlocked.approved_credits, Decimal('5.00'))


class StudentCourseAttemptAdminApiTests(
    StudentCourseAttemptFixtureMixin,
    APITestCase,
):
    endpoint = '/api/v1/admin/student-course-attempts/'

    def setUp(self) -> None:
        self.build_fixture()
        self.admin_user = User.objects.create_user(
            email='history.admin@unsa.edu.pe',
            password='Prueba123!',
        )
        self.admin_user.groups.add(
            Group.objects.get(name=Role.PLATFORM_ADMIN.value),
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_creates_passed_attempt_for_student(self) -> None:
        response = self.client.post(
            self.endpoint,
            {
                'student_id': str(self.student.public_id),
                'course_offering_id': str(self.previous_offering.public_id),
                'curriculum_course_id': str(self.previous_entry.public_id),
                'status': StudentCourseAttempt.Status.PASSED,
                'final_grade': '14.25',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['data']['final_grade'], '14.25')
        self.assertTrue(
            StudentCourseAttempt.objects.filter(
                student=self.student,
                status=StudentCourseAttempt.Status.PASSED,
            ).exists()
        )

    def test_rejects_passed_attempt_below_threshold(self) -> None:
        response = self.client.post(
            self.endpoint,
            {
                'student_id': str(self.student.public_id),
                'course_offering_id': str(self.previous_offering.public_id),
                'curriculum_course_id': str(self.previous_entry.public_id),
                'status': StudentCourseAttempt.Status.PASSED,
                'final_grade': '10.49',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('final_grade', response.json()['error']['errors'])
