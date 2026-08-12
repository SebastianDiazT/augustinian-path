import pytest

from apps.institution.models import Area, Faculty, ProfessionalSchool
from apps.institution.serializers import (
    AreaSerializer,
    FacultySerializer,
    ProfessionalSchoolSerializer,
)

pytestmark = pytest.mark.django_db


class TestInstitutionSerializers:
    def test_area_serializer_ignores_is_active_update(self):
        area = Area.objects.create(name='Ciencias', is_active=True)

        data = {'name': 'Ciencias Puras', 'is_active': False}
        serializer = AreaSerializer(area, data=data, partial=True)

        assert serializer.is_valid() is True
        updated_area = serializer.save()

        assert updated_area.name == 'Ciencias Puras'
        assert updated_area.is_active is True

    def test_faculty_serializer_enforces_unique_together(self):
        area = Area.objects.create(name='Ingenierías')
        Faculty.objects.create(area=area, name='Civil')

        data = {'area': str(area.public_id), 'name': 'Civil', 'code': 'CIV2'}
        serializer = FacultySerializer(data=data)

        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors

    def test_school_serializer_enforces_unique_together(self):
        area = Area.objects.create(name='Biomédicas')
        faculty = Faculty.objects.create(area=area, name='Ciencias de la Salud')
        ProfessionalSchool.objects.create(faculty=faculty, name='Nutrición')

        data = {'faculty': str(faculty.public_id), 'name': 'Nutrición', 'code': 'NUT2'}
        serializer = ProfessionalSchoolSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors

    def test_area_serializer_requires_name(self):
        data = {'code': 'INV'}
        serializer = AreaSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'name' in serializer.errors

    def test_faculty_serializer_rejects_inactive_area(self):
        area_inactiva = Area.objects.create(name='Área Antigua', is_active=False)

        data = {'area': str(area_inactiva.public_id), 'name': 'Nueva Facultad'}
        serializer = FacultySerializer(data=data)

        assert serializer.is_valid() is False
        assert 'area' in serializer.errors

    def test_school_serializer_rejects_invalid_uuid(self):
        data = {'faculty': 'no-es-un-uuid-valido', 'name': 'Escuela Falsa'}
        serializer = ProfessionalSchoolSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'faculty' in serializer.errors

    def test_area_serializer_enforces_max_length(self):
        data = {'name': 'A' * 151, 'code': 'CODE'}
        serializer = AreaSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'name' in serializer.errors
        assert serializer.errors['name'][0].code == 'max_length'

    def test_faculty_serializer_output_uses_slugs(self):
        area = Area.objects.create(name='Letras', code='LET')
        faculty = Faculty.objects.create(area=area, name='Filosofía', code='FIL')

        serializer = FacultySerializer(faculty)

        assert str(serializer.data['area']) == str(area.public_id)
        assert 'id' not in serializer.data
