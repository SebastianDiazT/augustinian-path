import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_timeblock_read_only(api_client, user_factory, time_block_factory):
    time_block_factory()
    user = user_factory()
    api_client.force_authenticate(user=user)

    url = reverse('offerings:time-block-list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    results = response.data.get('data', response.data)
    assert len(results) == 1

    response = api_client.post(url, data={})
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_offering_list_permissions(api_client, user_factory, offering_factory):
    offering_factory()
    user = user_factory()
    api_client.force_authenticate(user=user)

    url = reverse('offerings:offering-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_put_meetings_success(api_client, user_factory, section_factory, time_block_factory):
    admin_user = user_factory(is_platform_admin=True)
    api_client.force_authenticate(user=admin_user)

    section = section_factory(offering__course__lab_hours=2, section_type='lab')
    tb1 = time_block_factory(order=1)
    tb2 = time_block_factory(order=2)

    url = reverse('offerings:section-meetings', kwargs={'public_id': section.public_id})
    data = [
        {'day_of_week': 'monday', 'time_block': tb1.public_id, 'room': 'Lab A'},
        {'day_of_week': 'monday', 'time_block': tb2.public_id, 'room': 'Lab A'},
    ]

    response = api_client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert section.meetings.count() == 2


def test_put_meetings_transaction_rollback(
    api_client, user_factory, section_factory, time_block_factory, meeting_factory
):
    admin_user = user_factory(is_platform_admin=True)
    api_client.force_authenticate(user=admin_user)

    section = section_factory(
        offering__course__theory_hours=2,
        offering__course__practice_hours=0,
        offering__course__seminar_hours=0,
        offering__course__theory_practice_hours=0,
        section_type='theory',
    )
    tb_old = time_block_factory(order=1)
    tb_new = time_block_factory(order=2)

    meeting_factory(section=section, day_of_week='tuesday', time_block=tb_old)
    assert section.meetings.count() == 1

    url = reverse('offerings:section-meetings', kwargs={'public_id': section.public_id})

    bad_data = [
        {'day_of_week': 'monday', 'time_block': tb_new.public_id, 'room': 'Aula 1'},
        {'day_of_week': 'monday', 'time_block': tb_new.public_id, 'room': 'Aula 1'},
    ]

    response = api_client.put(url, bad_data, format='json')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    assert section.meetings.count() == 1
    assert section.meetings.first().time_block == tb_old


def test_permissions_create_update(
    api_client, user_factory, school_delegation_factory, offering_factory
):
    admin = user_factory(is_platform_admin=True)
    delegate = user_factory(is_platform_admin=False)
    random_user = user_factory(is_platform_admin=False)

    delegation = school_delegation_factory(delegate=delegate)
    school = delegation.school

    offering = offering_factory(course__curriculum_plan__school=school)

    url_list = reverse('offerings:offering-list')
    url_detail = reverse('offerings:offering-detail', kwargs={'public_id': offering.public_id})

    api_client.force_authenticate(user=random_user)
    assert api_client.post(url_list, {}).status_code == status.HTTP_403_FORBIDDEN
    assert api_client.patch(url_detail, {}).status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user=delegate)
    assert api_client.post(url_list, {}).status_code == status.HTTP_403_FORBIDDEN
    response = api_client.patch(url_detail, {'is_active': True}, format='json')
    assert response.status_code == status.HTTP_200_OK

    api_client.force_authenticate(user=admin)
    response_admin = api_client.patch(url_detail, {'is_active': False}, format='json')
    assert response_admin.status_code == status.HTTP_200_OK
