from datetime import time
from decimal import Decimal

from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

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
from apps.scheduling.models import (
    ClassMeeting,
    CourseSection,
    ScenarioSelection,
    ScheduleScenario,
)


class StudentSchedulingApiTests(APITestCase):
    scenario_endpoint = '/api/v1/scheduling/scenarios/'
    section_endpoint = '/api/v1/scheduling/sections/'

    def setUp(self) -> None:
        student_group = Group.objects.get(
            name=Role.STUDENT.value,
        )
        self.student = User.objects.create_user(
            email='student.schedule.api@unsa.edu.pe',
            password='Prueba123!',
        )
        self.student.groups.add(student_group)
        self.other_student = User.objects.create_user(
            email='other.schedule.api@unsa.edu.pe',
            password='Prueba123!',
        )
        self.other_student.groups.add(student_group)

        faculty = Faculty.objects.create(
            name='Facultad de Ingeniería',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=faculty,
            name='Ingeniería de Sistemas',
        )
        self.plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2017',
            name='Plan de Estudios 2017',
        )
        self.period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.FIRST,
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
        self.programming_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.programming,
            cycle=1,
            credits=Decimal('5.00'),
            theory_hours=Decimal('2.00'),
            laboratory_hours=Decimal('4.00'),
        )
        self.databases_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.databases,
            cycle=5,
            credits=Decimal('4.00'),
            theory_hours=Decimal('2.00'),
        )
        self.programming_offering = CourseOffering.objects.create(
            academic_period=self.period,
            course=self.programming,
        )
        self.programming_offering.curriculum_courses.add(
            self.programming_entry,
        )
        self.databases_offering = CourseOffering.objects.create(
            academic_period=self.period,
            course=self.databases,
        )
        self.databases_offering.curriculum_courses.add(
            self.databases_entry,
        )
        self.programming_theory = CourseSection.objects.create(
            course_offering=self.programming_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='A',
        )
        self.programming_lab = CourseSection.objects.create(
            course_offering=self.programming_offering,
            section_type=CourseSection.SectionType.LABORATORY,
            group_code='L1',
        )
        self.databases_theory = CourseSection.objects.create(
            course_offering=self.databases_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='B',
        )
        ClassMeeting.objects.create(
            section=self.programming_theory,
            day_of_week=ClassMeeting.DayOfWeek.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
            location='Aula 101',
        )
        ClassMeeting.objects.create(
            section=self.programming_lab,
            day_of_week=ClassMeeting.DayOfWeek.TUESDAY,
            start_time=time(8, 0),
            end_time=time(12, 0),
            location='Laboratorio 1',
        )
        ClassMeeting.objects.create(
            section=self.databases_theory,
            day_of_week=ClassMeeting.DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(11, 0),
            location='Aula 202',
        )
        self.scenario = ScheduleScenario.objects.create(
            user=self.student,
            academic_period=self.period,
            curriculum_plan=self.plan,
            name='Principal',
        )

    def authenticate(self) -> None:
        self.client.force_authenticate(user=self.student)

    def selection_endpoint(self) -> str:
        return f'{self.scenario_endpoint}{self.scenario.public_id}/selections/'

    def test_rejects_unauthenticated_scenario_list(self) -> None:
        response = self.client.get(self.scenario_endpoint)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_creates_scenario_for_current_student(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.scenario_endpoint,
            {
                'academic_period_id': str(self.period.public_id),
                'curriculum_plan_id': str(self.plan.public_id),
                'name': '  Alternativa   1 ',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['data']['name'], 'Alternativa 1')
        self.assertTrue(
            ScheduleScenario.objects.filter(
                user=self.student,
                name='Alternativa 1',
            ).exists()
        )

    def test_hides_scenario_owned_by_another_student(self) -> None:
        other_scenario = ScheduleScenario.objects.create(
            user=self.other_student,
            academic_period=self.period,
            curriculum_plan=self.plan,
            name='Privado',
        )
        self.authenticate()

        response = self.client.get(
            f'{self.scenario_endpoint}{other_scenario.public_id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lists_available_sections_for_plan_and_period(self) -> None:
        self.authenticate()

        response = self.client.get(
            f'{self.section_endpoint}?academic_period={self.period.public_id}'
            f'&curriculum_plan={self.plan.public_id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {section['id'] for section in response.json()['data']['course_sections']},
            {
                str(self.programming_theory.public_id),
                str(self.programming_lab.public_id),
                str(self.databases_theory.public_id),
            },
        )

    def test_reports_completed_hours_for_each_section(self) -> None:
        self.authenticate()

        response = self.client.get(
            f'{self.section_endpoint}?academic_period={self.period.public_id}'
            f'&curriculum_plan={self.plan.public_id}'
        )

        sections = {
            section['id']: section
            for section in response.json()['data']['course_sections']
        }
        theory = sections[str(self.programming_theory.public_id)]
        laboratory = sections[str(self.programming_lab.public_id)]

        self.assertEqual(theory['expected_hours'], '2.00')
        self.assertEqual(theory['scheduled_hours'], '2.00')
        self.assertTrue(theory['hours_complete'])
        self.assertEqual(laboratory['expected_hours'], '4.00')
        self.assertTrue(laboratory['hours_complete'])

    def test_rejects_meeting_that_exceeds_curriculum_hours(self) -> None:
        self.student.groups.add(
            Group.objects.get(name=Role.PLATFORM_ADMIN.value),
        )
        self.authenticate()

        response = self.client.post(
            '/api/v1/admin/class-meetings/',
            {
                'section_id': str(self.programming_theory.public_id),
                'day_of_week': ClassMeeting.DayOfWeek.FRIDAY,
                'start_time': '08:00',
                'end_time': '09:00',
                'location': 'Aula adicional',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', response.json()['error']['errors'])

    def test_requires_laboratory_when_curriculum_has_hours(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.selection_endpoint(),
            {
                'course_offering_id': str(self.programming_offering.public_id),
                'curriculum_course_id': str(self.programming_entry.public_id),
                'theory_section_id': str(self.programming_theory.public_id),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'laboratory_section_id',
            response.json()['error']['errors'],
        )

    def test_rejects_selection_with_incomplete_theory_hours(self) -> None:
        incomplete_theory = CourseSection.objects.create(
            course_offering=self.programming_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='C',
        )
        self.authenticate()

        response = self.client.post(
            self.selection_endpoint(),
            {
                'course_offering_id': str(self.programming_offering.public_id),
                'curriculum_course_id': str(self.programming_entry.public_id),
                'theory_section_id': str(incomplete_theory.public_id),
                'laboratory_section_id': str(self.programming_lab.public_id),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'theory_section_id',
            response.json()['error']['errors'],
        )

    def test_creates_selection_with_independent_laboratory(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.selection_endpoint(),
            {
                'course_offering_id': str(self.programming_offering.public_id),
                'curriculum_course_id': str(self.programming_entry.public_id),
                'theory_section_id': str(self.programming_theory.public_id),
                'laboratory_section_id': str(self.programming_lab.public_id),
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()['data']['theory_section']['id'],
            str(self.programming_theory.public_id),
        )
        self.assertEqual(
            response.json()['data']['laboratory_section']['id'],
            str(self.programming_lab.public_id),
        )

    def test_rejects_duplicate_class_meeting_with_standard_400(self) -> None:
        self.student.groups.add(
            Group.objects.get(
                name=Role.PLATFORM_ADMIN.value,
            )
        )
        self.authenticate()
        meetings_before = ClassMeeting.objects.count()

        response = self.client.post(
            '/api/v1/admin/class-meetings/',
            {
                'section_id': str(self.programming_theory.public_id),
                'day_of_week': ClassMeeting.DayOfWeek.MONDAY,
                'start_time': '08:00',
                'end_time': '10:00',
                'location': 'Otra aula',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.json()['error']['errors']['non_field_errors'],
            [
                'Ya existe una reunión con la misma sección, día y horario.',
            ],
        )
        self.assertEqual(
            ClassMeeting.objects.count(),
            meetings_before,
        )

    def test_returns_scenario_conflicts(self) -> None:
        ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.programming_offering,
            curriculum_course=self.programming_entry,
            theory_section=self.programming_theory,
            laboratory_section=self.programming_lab,
        )
        ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.databases_offering,
            curriculum_course=self.databases_entry,
            theory_section=self.databases_theory,
        )
        self.authenticate()

        response = self.client.get(
            f'{self.scenario_endpoint}{self.scenario.public_id}/conflicts/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['data']['has_conflicts'])
        self.assertEqual(len(response.json()['data']['conflicts']), 1)
        self.assertEqual(
            response.json()['data']['conflicts'][0]['overlap_start'],
            '09:00',
        )

    def test_blocks_and_unlocks_course_with_academic_history(self) -> None:
        self.databases_entry.prerequisite_credits = Decimal('5.00')
        self.databases_entry.save()
        CurriculumCoursePrerequisite.objects.create(
            curriculum_course=self.databases_entry,
            prerequisite=self.programming_entry,
        )
        self.authenticate()

        eligibility_endpoint = (
            '/api/v1/scheduling/eligibility/'
            f'?academic_period={self.period.public_id}'
            f'&curriculum_plan={self.plan.public_id}'
        )
        eligibility_response = self.client.get(eligibility_endpoint)
        eligibility_by_course = {
            result['course_code']: result
            for result in eligibility_response.json()['data']['course_eligibility']
        }

        self.assertFalse(eligibility_by_course['CS 201']['available'])
        self.assertEqual(
            eligibility_by_course['CS 201']['approved_credits'],
            '0.00',
        )

        blocked_response = self.client.post(
            self.selection_endpoint(),
            {
                'course_offering_id': str(self.databases_offering.public_id),
                'curriculum_course_id': str(self.databases_entry.public_id),
                'theory_section_id': str(self.databases_theory.public_id),
            },
            format='json',
        )

        self.assertEqual(
            blocked_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'bloqueada',
            str(blocked_response.json()['error']['errors']['curriculum_course_id']),
        )

        previous_period = AcademicPeriod.objects.create(
            year=2025,
            term=AcademicPeriod.Term.SECOND,
        )
        previous_offering = CourseOffering.objects.create(
            academic_period=previous_period,
            course=self.programming,
        )
        previous_offering.curriculum_courses.add(self.programming_entry)
        StudentCourseAttempt.objects.create(
            student=self.student,
            course_offering=previous_offering,
            curriculum_course=self.programming_entry,
            status=StudentCourseAttempt.Status.PASSED,
            final_grade=Decimal('10.50'),
        )

        unlocked_eligibility_response = self.client.get(
            eligibility_endpoint,
        )
        unlocked_eligibility_by_course = {
            result['course_code']: result
            for result in unlocked_eligibility_response.json()['data'][
                'course_eligibility'
            ]
        }

        self.assertTrue(
            unlocked_eligibility_by_course['CS 201']['available'],
        )

        unlocked_response = self.client.post(
            self.selection_endpoint(),
            {
                'course_offering_id': str(self.databases_offering.public_id),
                'curriculum_course_id': str(self.databases_entry.public_id),
                'theory_section_id': str(self.databases_theory.public_id),
            },
            format='json',
        )

        self.assertEqual(
            unlocked_response.status_code,
            status.HTTP_201_CREATED,
        )
