from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from apps.academics.models import (
    Course,
    CurriculumCourse,
    CurriculumCoursePrerequisite,
    CurriculumPlan,
    Faculty,
    ProfessionalSchool,
)


class FacultyTests(TestCase):
    def test_creates_active_faculty_with_public_id(self) -> None:
        faculty = Faculty.objects.create(
            name='Facultad de Ciencias Naturales y Formales',
        )

        self.assertIsInstance(faculty.public_id, UUID)
        self.assertTrue(faculty.is_active)
        self.assertIsNotNone(faculty.created_at)
        self.assertIsNotNone(faculty.updated_at)

    def test_normalizes_name_whitespace(self) -> None:
        faculty = Faculty.objects.create(
            name='  Facultad   de   Ingeniería  ',
        )

        self.assertEqual(
            faculty.name,
            'Facultad de Ingeniería',
        )

    def test_rejects_case_insensitive_duplicate_name(
        self,
    ) -> None:
        Faculty.objects.create(
            name='Facultad de Medicina',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Faculty.objects.create(
                    name='FACULTAD DE MEDICINA',
                )

    def test_rejects_empty_normalized_name(self) -> None:
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Faculty.objects.create(name='   ')

    def test_orders_faculties_by_name(self) -> None:
        Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        Faculty.objects.create(
            name='Facultad de Ciencias',
        )

        self.assertEqual(
            list(
                Faculty.objects.values_list(
                    'name',
                    flat=True,
                )
            ),
            [
                'Facultad de Ciencias',
                'Facultad de Ingenieria',
            ],
        )


class ProfessionalSchoolTests(TestCase):
    def setUp(self) -> None:
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )

    def test_creates_school_related_to_faculty(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertIsInstance(school.public_id, UUID)
        self.assertTrue(school.is_active)
        self.assertEqual(school.faculty, self.faculty)
        self.assertIn(
            school,
            self.faculty.professional_schools.all(),
        )

    def test_normalizes_name_whitespace(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='  Escuela   Profesional   de Sistemas  ',
        )

        self.assertEqual(
            school.name,
            'Escuela Profesional de Sistemas',
        )

    def test_rejects_duplicate_name_in_same_faculty(
        self,
    ) -> None:
        ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProfessionalSchool.objects.create(
                    faculty=self.faculty,
                    name='ESCUELA PROFESIONAL DE SISTEMAS',
                )

    def test_allows_same_name_in_different_faculty(
        self,
    ) -> None:
        other_faculty = Faculty.objects.create(
            name='Facultad de Ciencias',
        )

        first_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )
        second_school = ProfessionalSchool.objects.create(
            faculty=other_faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertNotEqual(
            first_school.public_id,
            second_school.public_id,
        )

    def test_protects_faculty_with_related_schools(
        self,
    ) -> None:
        ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        with self.assertRaises(ProtectedError):
            self.faculty.delete()

    def test_returns_descriptive_string(self) -> None:
        school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

        self.assertEqual(
            str(school),
            ('Escuela Profesional de Sistemas (Facultad de Ingenieria)'),
        )


class CurriculumPlanTests(TestCase):
    def setUp(self) -> None:
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

    def test_creates_plan_related_to_school(self) -> None:
        plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2017',
            name='Plan de Estudios 2017',
        )

        self.assertIsInstance(plan.public_id, UUID)
        self.assertTrue(plan.is_active)
        self.assertEqual(
            plan.professional_school,
            self.school,
        )
        self.assertIn(
            plan,
            self.school.curriculum_plans.all(),
        )

    def test_normalizes_code_and_name(self) -> None:
        plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='  plan   2025  ',
            name='  Plan   de   Estudios   2025  ',
        )

        self.assertEqual(plan.code, 'PLAN 2025')
        self.assertEqual(
            plan.name,
            'Plan de Estudios 2025',
        )

    def test_rejects_duplicate_code_in_same_school(
        self,
    ) -> None:
        CurriculumPlan.objects.create(
            professional_school=self.school,
            code='PLAN 2025',
            name='Primer plan',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CurriculumPlan.objects.create(
                    professional_school=self.school,
                    code='plan 2025',
                    name='Plan duplicado',
                )

    def test_allows_same_code_in_different_school(
        self,
    ) -> None:
        other_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Industrial',
        )

        first_plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2025',
            name='Plan de Sistemas',
        )
        second_plan = CurriculumPlan.objects.create(
            professional_school=other_school,
            code='2025',
            name='Plan de Industrial',
        )

        self.assertNotEqual(
            first_plan.public_id,
            second_plan.public_id,
        )

    def test_protects_school_with_related_plans(
        self,
    ) -> None:
        CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2025',
            name='Plan de Estudios 2025',
        )

        with self.assertRaises(ProtectedError):
            self.school.delete()

    def test_returns_descriptive_string(self) -> None:
        plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2025',
            name='Plan de Estudios 2025',
        )

        self.assertEqual(
            str(plan),
            ('2025 — Plan de Estudios 2025 (Escuela Profesional de Sistemas)'),
        )


class CourseTests(TestCase):
    def setUp(self) -> None:
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )

    def test_creates_course_related_to_school(self) -> None:
        course = Course.objects.create(
            professional_school=self.school,
            code='1701101',
            name='Programacion de Computadoras',
        )

        self.assertIsInstance(course.public_id, UUID)
        self.assertTrue(course.is_active)
        self.assertEqual(
            course.professional_school,
            self.school,
        )
        self.assertIn(
            course,
            self.school.courses.all(),
        )

    def test_normalizes_code_and_name(self) -> None:
        course = Course.objects.create(
            professional_school=self.school,
            code='  cs   101  ',
            name='  Programacion   de   Computadoras  ',
        )

        self.assertEqual(course.code, 'CS 101')
        self.assertEqual(
            course.name,
            'Programacion de Computadoras',
        )

    def test_rejects_duplicate_code_in_same_school(
        self,
    ) -> None:
        Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Primer curso',
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Course.objects.create(
                    professional_school=self.school,
                    code='cs 101',
                    name='Curso diferente',
                )

    def test_allows_same_code_in_different_school(
        self,
    ) -> None:
        other_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Industrial',
        )

        first_course = Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programacion',
        )
        second_course = Course.objects.create(
            professional_school=other_school,
            code='CS 101',
            name='Programacion',
        )

        self.assertNotEqual(
            first_course.public_id,
            second_course.public_id,
        )

    def test_allows_same_name_with_different_codes(
        self,
    ) -> None:
        first_course = Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programacion',
        )
        second_course = Course.objects.create(
            professional_school=self.school,
            code='CS 201',
            name='Programacion',
        )

        self.assertNotEqual(
            first_course.public_id,
            second_course.public_id,
        )

    def test_protects_school_with_related_courses(
        self,
    ) -> None:
        Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programacion',
        )

        with self.assertRaises(ProtectedError):
            self.school.delete()

    def test_returns_descriptive_string(self) -> None:
        course = Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programacion',
        )

        self.assertEqual(
            str(course),
            ('CS 101 — Programacion (Escuela Profesional de Sistemas)'),
        )


class CurriculumCourseTests(TestCase):
    def setUp(self) -> None:
        self.faculty = Faculty.objects.create(
            name='Facultad de Ingenieria',
        )
        self.school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Sistemas',
        )
        self.plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2025',
            name='Plan de Estudios 2025',
        )
        self.course = Course.objects.create(
            professional_school=self.school,
            code='CS 101',
            name='Programacion',
        )

    def test_adds_course_to_curriculum_plan(self) -> None:
        curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )

        self.assertIsInstance(
            curriculum_course.public_id,
            UUID,
        )
        self.assertEqual(
            curriculum_course.credits,
            Decimal('4.00'),
        )
        self.assertIn(
            curriculum_course,
            self.plan.curriculum_courses.all(),
        )
        self.assertIn(
            curriculum_course,
            self.course.curriculum_entries.all(),
        )

    def test_represents_curriculum_hours_and_component(self) -> None:
        curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            component=CurriculumCourse.Component.SPECIFIC_STUDIES,
            credits=Decimal('5.00'),
            prerequisite_credits=Decimal('20.00'),
            theory_hours=Decimal('2.00'),
            seminar_hours=Decimal('1.00'),
            theory_practice_hours=Decimal('1.00'),
            practice_hours=Decimal('2.00'),
            laboratory_hours=Decimal('4.00'),
        )

        self.assertEqual(
            curriculum_course.theory_schedule_hours,
            Decimal('6.00'),
        )
        self.assertTrue(curriculum_course.has_laboratory)
        self.assertEqual(
            curriculum_course.get_component_display(),
            'Estudios específicos',
        )

    def test_rejects_negative_curriculum_hours(self) -> None:
        curriculum_course = CurriculumCourse(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
            laboratory_hours=Decimal('-0.01'),
        )

        with self.assertRaises(ValidationError) as context:
            curriculum_course.full_clean()

        self.assertIn(
            'laboratory_hours',
            context.exception.message_dict,
        )

    def test_adds_prerequisite_from_same_curriculum_plan(self) -> None:
        prerequisite = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )
        advanced_course = Course.objects.create(
            professional_school=self.school,
            code='CS 201',
            name='Estructuras de Datos',
        )
        advanced_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=advanced_course,
            cycle=2,
            credits=Decimal('4.00'),
        )

        CurriculumCoursePrerequisite.objects.create(
            curriculum_course=advanced_entry,
            prerequisite=prerequisite,
        )

        self.assertEqual(
            list(advanced_entry.prerequisites.all()),
            [prerequisite],
        )
        self.assertEqual(
            list(prerequisite.required_by.all()),
            [advanced_entry],
        )

    def test_rejects_prerequisite_from_another_plan(self) -> None:
        prerequisite = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )
        other_plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2026',
            name='Plan de Estudios 2026',
        )
        advanced_course = Course.objects.create(
            professional_school=self.school,
            code='CS 201',
            name='Estructuras de Datos',
        )
        advanced_entry = CurriculumCourse.objects.create(
            curriculum_plan=other_plan,
            course=advanced_course,
            cycle=2,
            credits=Decimal('4.00'),
        )

        with self.assertRaises(ValidationError) as context:
            CurriculumCoursePrerequisite.objects.create(
                curriculum_course=advanced_entry,
                prerequisite=prerequisite,
            )

        self.assertIn(
            'prerequisite',
            context.exception.message_dict,
        )

    def test_rejects_self_as_prerequisite(self) -> None:
        curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )

        with self.assertRaises(ValidationError) as context:
            CurriculumCoursePrerequisite.objects.create(
                curriculum_course=curriculum_course,
                prerequisite=curriculum_course,
            )

        self.assertIn(
            'prerequisite',
            context.exception.message_dict,
        )

    def test_rejects_course_from_different_school(
        self,
    ) -> None:
        other_school = ProfessionalSchool.objects.create(
            faculty=self.faculty,
            name='Escuela Profesional de Industrial',
        )
        other_course = Course.objects.create(
            professional_school=other_school,
            code='IN 101',
            name='Introduccion a Industrial',
        )

        with self.assertRaises(ValidationError) as context:
            CurriculumCourse.objects.create(
                curriculum_plan=self.plan,
                course=other_course,
                cycle=1,
                credits=Decimal('3.00'),
            )

        self.assertIn(
            'course',
            context.exception.message_dict,
        )

    def test_rejects_duplicate_course_in_same_plan(
        self,
    ) -> None:
        CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )

        with self.assertRaises(ValidationError):
            CurriculumCourse.objects.create(
                curriculum_plan=self.plan,
                course=self.course,
                cycle=2,
                credits=Decimal('4.00'),
            )

    def test_allows_course_in_different_plans(
        self,
    ) -> None:
        other_plan = CurriculumPlan.objects.create(
            professional_school=self.school,
            code='2026',
            name='Plan de Estudios 2026',
        )

        first_entry = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )
        second_entry = CurriculumCourse.objects.create(
            curriculum_plan=other_plan,
            course=self.course,
            cycle=2,
            credits=Decimal('3.50'),
        )

        self.assertNotEqual(
            first_entry.public_id,
            second_entry.public_id,
        )

    def test_rejects_cycle_zero(self) -> None:
        with self.assertRaises(ValidationError):
            CurriculumCourse.objects.create(
                curriculum_plan=self.plan,
                course=self.course,
                cycle=0,
                credits=Decimal('4.00'),
            )

    def test_rejects_negative_credits(self) -> None:
        with self.assertRaises(ValidationError):
            CurriculumCourse.objects.create(
                curriculum_plan=self.plan,
                course=self.course,
                cycle=1,
                credits=Decimal('-1.00'),
            )

    def test_protects_plan_and_course(self) -> None:
        CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )

        with self.assertRaises(ProtectedError):
            self.plan.delete()

        with self.assertRaises(ProtectedError):
            self.course.delete()

    def test_returns_descriptive_string(self) -> None:
        curriculum_course = CurriculumCourse.objects.create(
            curriculum_plan=self.plan,
            course=self.course,
            cycle=1,
            credits=Decimal('4.00'),
        )

        self.assertEqual(
            str(curriculum_course),
            '2025: CS 101 — ciclo 1',
        )
