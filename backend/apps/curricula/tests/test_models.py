import pytest
from django.core.exceptions import ValidationError

from apps.curricula.models import (
    AcademicTerm,
    Course,
    CurriculumPlan,
    ElectiveBranch,
    EvaluationComponent,
    Instructor,
    Prerequisite,
    Syllabus,
)
from apps.institution.models import Area, Faculty, ProfessionalSchool

pytestmark = pytest.mark.django_db


class TestCurriculaModels:
    @pytest.fixture
    def setup_data(self):
        area = Area.objects.create(name='Area')
        faculty = Faculty.objects.create(area=area, name='Fac')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='School')
        plan = CurriculumPlan.objects.create(school=school, year='2026')
        return school, plan

    def test_string_representations_and_properties(self, setup_data):
        school, plan = setup_data
        assert str(plan) == f'{school} — 2026'

        branch = ElectiveBranch.objects.create(curriculum_plan=plan, name='AI')
        assert str(branch) == f'{plan} — AI'
        assert branch.get_school() == school

        course = Course.objects.create(
            curriculum_plan=plan,
            code='C1',
            name='C1',
            credits=3,
            cycle=1,
            course_type='mandatory',
            academic_area='specialty',
            lab_hours=2,
        )
        assert str(course) == 'C1 — C1'
        assert course.get_school() == school
        assert course.has_lab is True

        course2 = Course.objects.create(
            curriculum_plan=plan,
            code='C2',
            name='C2',
            credits=3,
            cycle=2,
            course_type='mandatory',
            academic_area='specialty',
        )
        prereq = Prerequisite.objects.create(course=course2, required_course=course)
        assert str(prereq) == f'{course2} requiere {course}'
        assert prereq.get_school() == school

        term = AcademicTerm.objects.create(
            code='2026-A',
            start_date='2026-01-01',
            end_date='2026-06-01',
        )
        assert str(term) == '2026-A'

        instructor = Instructor.objects.create(full_name='Prof')
        assert str(instructor) == 'Prof'

        syllabus = Syllabus.objects.create(course=course, academic_term=term)
        assert str(syllabus) == f'{course} — {term}'
        assert syllabus.get_school() == school

        comp = EvaluationComponent.objects.create(
            syllabus=syllabus, name='Exam', weight=50.5, order=1
        )
        assert str(comp) == 'Exam (50.5%)'

    def test_prerequisite_clean_validations(self, setup_data):
        school, plan1 = setup_data
        plan2 = CurriculumPlan.objects.create(school=school, year='2027')

        c1 = Course.objects.create(curriculum_plan=plan1, code='A', name='A', credits=1, cycle=1)
        c2 = Course.objects.create(curriculum_plan=plan2, code='B', name='B', credits=1, cycle=1)

        with pytest.raises(ValidationError):
            Prerequisite(course=c1, required_course=c1).clean()

        with pytest.raises(ValidationError):
            Prerequisite(course=c1, required_course=c2).clean()
