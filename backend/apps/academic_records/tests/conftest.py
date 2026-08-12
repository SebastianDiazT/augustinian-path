import datetime
from decimal import Decimal

import factory
import pytest
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.academic_records.models import CourseEnrollment, Grade
from apps.accounts.models import StudentProfile
from apps.curricula.models import (
    AcademicTerm,
    Course,
    CurriculumPlan,
    EvaluationComponent,
    Instructor,
    Syllabus,
)
from apps.institution.models import Area, Faculty, ProfessionalSchool
from apps.offerings.models import Offering, Section

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


if not hasattr(CurriculumPlan, 'total_credits_required'):

    def get_credits(self):
        return getattr(self, '_mock_credits', Decimal('200.0'))

    def set_credits(self, val):
        self._mock_credits = val

    CurriculumPlan.total_credits_required = property(get_credits, set_credits)

if not hasattr(CurriculumPlan, 'min_elective_branches_to_complete'):

    def get_branches(self):
        return getattr(self, '_mock_branches', 1)

    def set_branches(self, val):
        self._mock_branches = val

    CurriculumPlan.min_elective_branches_to_complete = property(get_branches, set_branches)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'student{n}@unsa.edu.pe')
    is_platform_admin = False


class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory(UserFactory)
    cui = factory.Sequence(lambda n: f'2026{n:05d}')


class AreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.Sequence(lambda n: f'Area {n}')


class FacultyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Faculty

    name = factory.Sequence(lambda n: f'Facultad {n}')
    area = factory.SubFactory(AreaFactory)


class ProfessionalSchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProfessionalSchool

    name = factory.Sequence(lambda n: f'Escuela {n}')
    faculty = factory.SubFactory(FacultyFactory)


class CurriculumPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CurriculumPlan

    school = factory.SubFactory(ProfessionalSchoolFactory)
    year = 2026


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = factory.Sequence(lambda n: f'Curso {n}')
    code = factory.Sequence(lambda n: f'CS{n:03d}')
    curriculum_plan = factory.SubFactory(CurriculumPlanFactory)
    credits = Decimal('4.0')
    cycle = 1
    theory_hours = 2
    practice_hours = 0
    lab_hours = 0
    seminar_hours = 0
    theory_practice_hours = 0


class AcademicTermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AcademicTerm

    code = factory.Sequence(lambda n: f'2026-{n}')
    start_date = datetime.date(2026, 3, 23)
    end_date = datetime.date(2026, 7, 24)


class SyllabusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Syllabus

    course = factory.SubFactory(CourseFactory)
    academic_term = factory.SubFactory(AcademicTermFactory)


class EvaluationComponentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EvaluationComponent

    syllabus = factory.SubFactory(SyllabusFactory)
    name = factory.Sequence(lambda n: f'Fase {n}')
    weight = Decimal('33.33')
    order = factory.Sequence(lambda n: n)


class OfferingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offering

    course = factory.SubFactory(CourseFactory)
    academic_term = factory.SubFactory(AcademicTermFactory)


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section

    offering = factory.SubFactory(OfferingFactory)
    instructor = factory.SubFactory(InstructorFactory)
    section_type = 'theory'
    number = factory.Sequence(lambda n: f'A{n}')


class CourseEnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseEnrollment

    student = factory.SubFactory(StudentProfileFactory)
    offering = factory.SubFactory(OfferingFactory)
    theory_section = factory.SubFactory(SectionFactory)
    status = CourseEnrollment.Status.IN_PROGRESS


class GradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grade

    enrollment = factory.SubFactory(CourseEnrollmentFactory)
    evaluation_component = factory.SubFactory(EvaluationComponentFactory)
    score = Decimal('15.00')


register(UserFactory)
register(StudentProfileFactory)
register(AreaFactory)
register(FacultyFactory)
register(ProfessionalSchoolFactory)
register(CurriculumPlanFactory)
register(CourseFactory)
register(AcademicTermFactory)
register(SyllabusFactory)
register(EvaluationComponentFactory)
register(OfferingFactory)
register(InstructorFactory)
register(SectionFactory)
register(CourseEnrollmentFactory)
register(GradeFactory)
