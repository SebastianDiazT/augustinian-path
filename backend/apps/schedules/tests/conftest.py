import datetime
from decimal import Decimal

import factory
import pytest
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.accounts.models import StudentProfile
from apps.curricula.models import AcademicTerm, Course, CurriculumPlan, Instructor
from apps.institution.models import Area, Faculty, ProfessionalSchool
from apps.offerings.models import Meeting, Offering, Section, TimeBlock
from apps.schedules.models import (
    PublicShareLink,
    ScheduleAlternative,
    ScheduleSimulation,
)

User = get_user_model()

if not hasattr(Course, 'has_lab'):

    def get_has_lab(self):
        return getattr(self, '_mock_has_lab', False)

    def set_has_lab(self, val):
        self._mock_has_lab = val

    Course.has_lab = property(get_has_lab, set_has_lab)


@pytest.fixture
def api_client():
    return APIClient()


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


class AcademicTermFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AcademicTerm

    code = factory.Sequence(lambda n: f'2026-{n}')
    start_date = datetime.date(2026, 3, 23)
    end_date = datetime.date(2026, 7, 24)


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


class OfferingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offering

    course = factory.SubFactory(CourseFactory)
    academic_term = factory.SubFactory(AcademicTermFactory)


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor

    full_name = factory.Sequence(lambda n: f'Prof {n} Doe')


class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section

    offering = factory.SubFactory(OfferingFactory)
    instructor = factory.SubFactory(InstructorFactory)
    section_type = 'theory'
    number = factory.Sequence(lambda n: f'A{n}')


class TimeBlockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeBlock

    order = factory.Sequence(lambda n: n % 16 + 1)
    start_time = datetime.time(7, 0)
    end_time = datetime.time(7, 50)


class MeetingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meeting

    section = factory.SubFactory(SectionFactory)
    time_block = factory.SubFactory(TimeBlockFactory)
    day_of_week = 'monday'
    room = 'A-101'


class ScheduleSimulationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScheduleSimulation

    student = factory.SubFactory(StudentProfileFactory)
    academic_term = factory.SubFactory(AcademicTermFactory)


class ScheduleAlternativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScheduleAlternative

    simulation = factory.SubFactory(ScheduleSimulationFactory)
    score = Decimal('85.00')
    rank = 1


class PublicShareLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PublicShareLink

    alternative = factory.SubFactory(ScheduleAlternativeFactory)


register(UserFactory)
register(StudentProfileFactory)
register(AcademicTermFactory)
register(CourseFactory)
register(OfferingFactory)
register(InstructorFactory)
register(SectionFactory)
register(TimeBlockFactory)
register(MeetingFactory)
register(ScheduleSimulationFactory)
register(ScheduleAlternativeFactory)
register(PublicShareLinkFactory)
