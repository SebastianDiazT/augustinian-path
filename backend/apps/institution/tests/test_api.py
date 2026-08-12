import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import SchoolDelegation, User
from apps.institution.models import Area, Faculty, ProfessionalSchool

pytestmark = pytest.mark.django_db


@pytest.fixture
def platform_admin():
    return User.objects.create_user(
        email='admin@unsa.edu.pe', full_name='Admin', is_platform_admin=True
    )


@pytest.fixture
def normal_student():
    return User.objects.create_user(email='estudiante@unsa.edu.pe', full_name='Estudiante Normal')


@pytest.fixture
def populated_institution():
    area = Area.objects.create(name='Ingenierías', code='ING')
    faculty = Faculty.objects.create(area=area, name='Producción', code='FIPS')
    school_1 = ProfessionalSchool.objects.create(faculty=faculty, name='Sistemas', code='EPIS')
    school_2 = ProfessionalSchool.objects.create(faculty=faculty, name='Industrial', code='EPII')
    return area, faculty, school_1, school_2


@pytest.fixture
def delegate_user(populated_institution):
    _, _, school_1, _ = populated_institution
    delegate = User.objects.create_user(email='delegado@unsa.edu.pe', full_name='Delegado')
    SchoolDelegation.objects.create(delegate=delegate, school=school_1)
    return delegate


def test_unauthenticated_user_cannot_read_catalog():
    client = APIClient()
    response = client.get(reverse('institution:area-list'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_normal_student_can_read_catalog(normal_student, populated_institution):
    client = APIClient()
    client.force_authenticate(normal_student)
    response = client.get(reverse('institution:area-list'))
    assert response.status_code == status.HTTP_200_OK
    assert 'data' in response.data


def test_student_cannot_create_area(normal_student):
    client = APIClient()
    client.force_authenticate(normal_student)
    payload = {'name': 'Sociales', 'code': 'SOC', 'is_active': True}
    response = client.post(reverse('institution:area-list'), payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delegate_can_update_own_school_but_not_others(delegate_user, populated_institution):
    _, _, school_own, school_other = populated_institution
    client = APIClient()
    client.force_authenticate(delegate_user)

    res_own = client.patch(
        reverse('institution:professional-school-detail', args=[school_own.public_id]),
        {'name': 'Actualizada'},
    )
    assert res_own.status_code == status.HTTP_200_OK

    res_other = client.patch(
        reverse('institution:professional-school-detail', args=[school_other.public_id]),
        {'name': 'Hackeada'},
    )
    assert res_other.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_update_any_school(platform_admin, populated_institution):
    _, _, school_1, _ = populated_institution
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.patch(
        reverse('institution:professional-school-detail', args=[school_1.public_id]),
        {'name': 'Supremo'},
    )
    assert response.status_code == status.HTTP_200_OK


def test_admin_full_creation_cascade_flow(platform_admin):
    client = APIClient()
    client.force_authenticate(platform_admin)

    res_area = client.post(
        reverse('institution:area-list'), {'name': 'Biomédicas', 'code': 'BIO', 'is_active': True}
    )
    assert res_area.status_code == status.HTTP_201_CREATED
    area_id = res_area.data['public_id']

    res_faculty = client.post(
        reverse('institution:faculty-list'),
        {'area': area_id, 'name': 'Medicina', 'code': 'FMED', 'is_active': True},
    )
    assert res_faculty.status_code == status.HTTP_201_CREATED
    faculty_id = res_faculty.data['public_id']

    res_school = client.post(
        reverse('institution:professional-school-list'),
        {'faculty': faculty_id, 'name': 'Enfermería', 'code': 'ENF', 'is_active': True},
    )
    assert res_school.status_code == status.HTTP_201_CREATED


def test_api_blocks_soft_delete_with_active_children(platform_admin, populated_institution):
    area, _, _, _ = populated_institution
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.delete(reverse('institution:area-detail', args=[area.public_id]))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert response.data['error']['code'] == 'VALIDATION_ERROR'
    assert any(d['field'] == 'detail' for d in response.data['error']['details'])


def test_api_blocks_faculty_soft_delete_with_active_schools(platform_admin, populated_institution):
    _, faculty, _, _ = populated_institution
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.delete(reverse('institution:faculty-detail', args=[faculty.public_id]))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error']['code'] == 'VALIDATION_ERROR'


def test_api_allows_soft_delete_for_leaf_nodes(platform_admin, populated_institution):
    _, _, school_1, _ = populated_institution
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.delete(
        reverse('institution:professional-school-detail', args=[school_1.public_id])
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    school_1.refresh_from_db()
    assert school_1.is_active is False


def test_inactive_records_do_not_appear_in_list(platform_admin):
    Area.objects.create(name='Activa', is_active=True)
    Area.objects.create(name='Inactiva', is_active=False)

    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.get(reverse('institution:area-list'))

    items = response.data['data']
    assert len(items) == 1
    assert items[0]['name'] == 'Activa'


def test_cannot_retrieve_inactive_object(platform_admin):
    area = Area.objects.create(name='Área Fantasma', is_active=False)
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.get(reverse('institution:area-detail', args=[area.public_id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_update_inactive_object(platform_admin):
    area = Area.objects.create(name='Área Antigua', is_active=False)
    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.patch(
        reverse('institution:area-detail', args=[area.public_id]), {'name': 'Intento'}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_duplicate_faculty_returns_standard_error(platform_admin, populated_institution):
    area, _, _, _ = populated_institution
    client = APIClient()
    client.force_authenticate(platform_admin)

    client.post(reverse('institution:faculty-list'), {'area': area.public_id, 'name': 'Repetida'})
    response = client.post(
        reverse('institution:faculty-list'), {'area': area.public_id, 'name': 'Repetida'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert response.data['error']['code'] == 'VALIDATION_ERROR'
    assert any(d['field'] == 'non_field_errors' for d in response.data['error']['details'])


def test_api_allows_soft_delete_for_empty_area(platform_admin):
    area_vacia = Area.objects.create(name='Área Vacía', is_active=True)

    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.delete(reverse('institution:area-detail', args=[area_vacia.public_id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    area_vacia.refresh_from_db()
    assert area_vacia.is_active is False


def test_api_allows_soft_delete_for_empty_faculty(platform_admin):
    area = Area.objects.create(name='Área Prueba')
    facultad_vacia = Faculty.objects.create(area=area, name='Facultad Vacía', is_active=True)

    client = APIClient()
    client.force_authenticate(platform_admin)
    response = client.delete(reverse('institution:faculty-detail', args=[facultad_vacia.public_id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    facultad_vacia.refresh_from_db()
    assert facultad_vacia.is_active is False


def test_normal_student_can_read_faculties_and_schools(normal_student, populated_institution):
    client = APIClient()
    client.force_authenticate(normal_student)

    res_faculties = client.get(reverse('institution:faculty-list'))
    assert res_faculties.status_code == status.HTTP_200_OK

    res_schools = client.get(reverse('institution:professional-school-list'))
    assert res_schools.status_code == status.HTTP_200_OK