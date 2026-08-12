import pytest

from apps.institution.models import Area, Faculty, ProfessionalSchool

pytestmark = pytest.mark.django_db


class TestCoreModels:
    def test_active_manager_hides_deleted_records(self):
        area = Area.objects.create(name='Ingenierías')
        faculty = Faculty.objects.create(area=area, name='Sistemas')

        ProfessionalSchool.objects.create(faculty=faculty, name='Escuela Activa')

        ProfessionalSchool.objects.create(faculty=faculty, name='Escuela Borrada', is_active=False)

        assert ProfessionalSchool.objects.count() == 1
        assert ProfessionalSchool.objects.first().name == 'Escuela Activa'

        assert ProfessionalSchool.all_objects.count() == 2
