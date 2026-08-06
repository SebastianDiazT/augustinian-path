from datetime import time
from decimal import Decimal

from django.core.exceptions import ValidationError
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
from apps.accounts.models import User
from apps.scheduling.models import (
    ClassMeeting,
    CourseSection,
    ScenarioSelection,
    ScheduleScenario,
)
from apps.scheduling.services import detect_schedule_conflicts


class SchedulingModelTests(TestCase):
    def setUp(self) -> None:
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
        self.other_period = AcademicPeriod.objects.create(
            year=2026,
            term=AcademicPeriod.Term.SECOND,
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
            laboratory_hours=Decimal('4.00'),
        )
        self.databases_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.databases,
            cycle=5,
            credits=Decimal('4.00'),
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
            group_code=' a ',
        )
        self.programming_laboratory = CourseSection.objects.create(
            course_offering=self.programming_offering,
            section_type=CourseSection.SectionType.LABORATORY,
            group_code=' l1 ',
        )
        self.databases_theory = CourseSection.objects.create(
            course_offering=self.databases_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='B',
        )
        ClassMeeting.objects.create(
            section=self.programming_laboratory,
            day_of_week=ClassMeeting.DayOfWeek.TUESDAY,
            start_time=time(8, 0),
            end_time=time(12, 0),
        )
        self.user = User.objects.create_user(
            email='student.scheduling@unsa.edu.pe',
            password='Prueba123!',
        )
        self.scenario = ScheduleScenario.objects.create(
            user=self.user,
            academic_period=self.period,
            curriculum_plan=self.plan,
            name='  Horario   principal  ',
        )

    def test_normalizes_section_and_scenario_names(self) -> None:
        self.assertEqual(self.programming_theory.group_code, 'A')
        self.assertEqual(self.programming_laboratory.group_code, 'L1')
        self.assertEqual(self.scenario.name, 'Horario principal')

    def test_rejects_duplicate_section_group_case_insensitively(self) -> None:
        with self.assertRaises(ValidationError):
            CourseSection.objects.create(
                course_offering=self.programming_offering,
                section_type=CourseSection.SectionType.THEORY,
                group_code='a',
            )

    def test_rejects_laboratory_for_course_without_laboratory_hours(self) -> None:
        with self.assertRaises(ValidationError) as context:
            CourseSection.objects.create(
                course_offering=self.databases_offering,
                section_type=CourseSection.SectionType.LABORATORY,
                group_code='L1',
            )

        self.assertIn('section_type', context.exception.message_dict)

    def test_rejects_meeting_with_invalid_interval(self) -> None:
        with self.assertRaises(ValidationError) as context:
            ClassMeeting.objects.create(
                section=self.programming_theory,
                day_of_week=ClassMeeting.DayOfWeek.MONDAY,
                start_time=time(10, 0),
                end_time=time(9, 0),
            )

        self.assertIn('end_time', context.exception.message_dict)

    def test_requires_laboratory_selection_from_curriculum(self) -> None:
        with self.assertRaises(ValidationError) as context:
            ScenarioSelection.objects.create(
                scenario=self.scenario,
                course_offering=self.programming_offering,
                curriculum_course=self.programming_entry,
                theory_section=self.programming_theory,
            )

        self.assertIn('laboratory_section', context.exception.message_dict)

    def test_creates_theory_and_laboratory_selection(self) -> None:
        selection = ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.programming_offering,
            curriculum_course=self.programming_entry,
            theory_section=self.programming_theory,
            laboratory_section=self.programming_laboratory,
        )

        self.assertEqual(selection.theory_section, self.programming_theory)
        self.assertEqual(
            selection.laboratory_section,
            self.programming_laboratory,
        )

    def test_rejects_offering_from_another_period(self) -> None:
        other_offering = CourseOffering.objects.create(
            academic_period=self.other_period,
            course=self.databases,
        )
        other_offering.curriculum_courses.add(self.databases_entry)
        other_theory = CourseSection.objects.create(
            course_offering=other_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='A',
        )

        with self.assertRaises(ValidationError) as context:
            ScenarioSelection.objects.create(
                scenario=self.scenario,
                course_offering=other_offering,
                curriculum_course=self.databases_entry,
                theory_section=other_theory,
            )

        self.assertIn('course_offering', context.exception.message_dict)

    def test_rejects_duplicate_offering_in_scenario(self) -> None:
        ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.databases_offering,
            curriculum_course=self.databases_entry,
            theory_section=self.databases_theory,
        )

        with self.assertRaises(ValidationError):
            ScenarioSelection.objects.create(
                scenario=self.scenario,
                course_offering=self.databases_offering,
                curriculum_course=self.databases_entry,
                theory_section=self.databases_theory,
            )

    def test_detects_overlapping_meetings_but_not_adjacent_ones(self) -> None:
        self.programming_entry.theory_hours = Decimal('2.00')
        self.programming_entry.save()
        self.databases_entry.theory_hours = Decimal('1.00')
        self.databases_entry.save()
        ClassMeeting.objects.create(
            section=self.programming_theory,
            day_of_week=ClassMeeting.DayOfWeek.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        ClassMeeting.objects.create(
            section=self.databases_theory,
            day_of_week=ClassMeeting.DayOfWeek.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        adjacent_section = CourseSection.objects.create(
            course_offering=self.databases_offering,
            section_type=CourseSection.SectionType.THEORY,
            group_code='C',
        )
        ClassMeeting.objects.create(
            section=adjacent_section,
            day_of_week=ClassMeeting.DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )
        ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.programming_offering,
            curriculum_course=self.programming_entry,
            theory_section=self.programming_theory,
            laboratory_section=self.programming_laboratory,
        )
        ScenarioSelection.objects.create(
            scenario=self.scenario,
            course_offering=self.databases_offering,
            curriculum_course=self.databases_entry,
            theory_section=self.databases_theory,
        )

        conflicts = detect_schedule_conflicts(self.scenario)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].overlap_start, time(9, 0))
        self.assertEqual(conflicts[0].overlap_end, time(10, 0))
