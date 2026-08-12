import datetime

import factory
import pytest
from django.contrib.auth import get_user_model
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.accounts.models import SchoolDelegation
from apps.curricula.models import AcademicTerm, Course, CurriculumPlan, Instructor
from apps.institution.models import Area, Faculty, ProfessionalSchool
from apps.offerings.models import Meeting, Offering, Section, TimeBlock

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@unsa.edu.pe')
    is_platform_admin = False


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


class SchoolDelegationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchoolDelegation

    delegate = factory.SubFactory(UserFactory)
    school = factory.SubFactory(ProfessionalSchoolFactory)


class CurriculumPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CurriculumPlan

    school = factory.SubFactory(ProfessionalSchoolFactory)
    year = 2026


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    name = factory.Sequence(lambda n: f'Curso {n}')
    curriculum_plan = factory.SubFactory(CurriculumPlanFactory)
    credits = 4
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


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor

    full_name = 'Mayte Sofia'


class OfferingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offering

    course = factory.SubFactory(CourseFactory)
    academic_term = factory.SubFactory(AcademicTermFactory)


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

    order = factory.Sequence(lambda n: n)
    start_time = datetime.time(7, 0)
    end_time = datetime.time(7, 50)


class MeetingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meeting

    section = factory.SubFactory(SectionFactory)
    day_of_week = 'monday'
    time_block = factory.SubFactory(TimeBlockFactory)


register(UserFactory)
register(AreaFactory)
register(FacultyFactory)
register(ProfessionalSchoolFactory)
register(SchoolDelegationFactory)
register(CurriculumPlanFactory)
register(CourseFactory)
register(AcademicTermFactory)
register(InstructorFactory)
register(OfferingFactory)
register(SectionFactory)
register(TimeBlockFactory)
register(MeetingFactory)
