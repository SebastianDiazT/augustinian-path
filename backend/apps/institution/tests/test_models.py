import pytest
from django.db import IntegrityError

from apps.institution.models import Area, Faculty, ProfessionalSchool

pytestmark = pytest.mark.django_db


class TestInstitutionModels:
    def test_area_string_representation(self):
        area = Area.objects.create(name='Biomédicas', code='BIO')
        assert str(area) == 'Biomédicas'

    def test_faculty_string_representation(self):
        area = Area.objects.create(name='Biomédicas', code='BIO')
        faculty = Faculty.objects.create(area=area, name='Medicina', code='FMED')
        assert str(faculty) == 'Medicina'

    def test_professional_school_string_representation(self):
        area = Area.objects.create(name='Biomédicas', code='BIO')
        faculty = Faculty.objects.create(area=area, name='Medicina', code='FMED')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='Enfermería', code='ENF')
        assert str(school) == 'Enfermería'

    def test_professional_school_get_school_returns_itself(self):
        area = Area.objects.create(name='Ingenierías')
        faculty = Faculty.objects.create(area=area, name='Sistemas')
        school = ProfessionalSchool.objects.create(faculty=faculty, name='Ingeniería de Sistemas')
        assert school.get_school() == school

    def test_faculty_unique_constraint_per_area(self):
        area = Area.objects.create(name='Sociales')
        Faculty.objects.create(area=area, name='Derecho')

        with pytest.raises(IntegrityError):
            Faculty.objects.create(area=area, name='Derecho')

    def test_faculty_allows_same_name_in_different_areas(self):
        area_1 = Area.objects.create(name='Sede Central')
        area_2 = Area.objects.create(name='Sede Sur')

        Faculty.objects.create(area=area_1, name='Administración')
        Faculty.objects.create(area=area_2, name='Administración')

    def test_school_unique_constraint_per_faculty(self):
        area = Area.objects.create(name='Ingenierías')
        faculty = Faculty.objects.create(area=area, name='Producción')
        ProfessionalSchool.objects.create(faculty=faculty, name='Sistemas')

        with pytest.raises(IntegrityError):
            ProfessionalSchool.objects.create(faculty=faculty, name='Sistemas')
