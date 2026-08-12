from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_generate_simulation_endpoint(api_client, student_profile_factory, offering_factory):
    student = student_profile_factory()
    api_client.force_authenticate(user=student.user)
    offering = offering_factory()

    url = reverse('schedules:schedule-simulation-generate')

    assert api_client.post(url, {}).status_code == status.HTTP_400_BAD_REQUEST

    payload = {
        'academic_term': offering.academic_term.public_id,
        'offerings': [offering.public_id],
        'preferences': {'maximize_free_days': True},
    }

    with patch('apps.schedules.views.run_simulation', return_value=[]) as mock_run:
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert mock_run.called


def test_simulation_read_permissions(api_client, user_factory, schedule_simulation_factory):
    sim = schedule_simulation_factory()
    url_list = reverse('schedules:schedule-simulation-list')
    url_detail = reverse(
        'schedules:schedule-simulation-detail', kwargs={'public_id': sim.public_id}
    )

    other_student = user_factory()
    api_client.force_authenticate(user=other_student)
    assert api_client.get(url_list).data.get('count', 0) == 0
    assert api_client.get(url_detail).status_code == status.HTTP_404_NOT_FOUND

    api_client.force_authenticate(user=sim.student.user)
    assert api_client.get(url_detail).status_code == status.HTTP_200_OK

    admin = user_factory(is_platform_admin=True)
    api_client.force_authenticate(user=admin)
    assert api_client.get(url_detail).status_code == status.HTTP_200_OK


def test_toggle_favorite_action(api_client, schedule_alternative_factory):
    alt = schedule_alternative_factory(is_favorite=False)
    api_client.force_authenticate(user=alt.simulation.student.user)

    url = reverse(
        'schedules:schedule-alternative-toggle-favorite', kwargs={'public_id': alt.public_id}
    )
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    alt.refresh_from_db()
    assert alt.is_favorite is True


def test_public_share_flow(api_client, schedule_alternative_factory):
    alt = schedule_alternative_factory()
    student_user = alt.simulation.student.user
    api_client.force_authenticate(user=student_user)

    create_url = reverse('schedules:share-link-list')
    res_create = api_client.post(
        create_url, {'alternative': alt.public_id, 'include_personal_info': True}, format='json'
    )
    assert res_create.status_code == status.HTTP_201_CREATED
    public_id = res_create.data['public_id']

    api_client.force_authenticate(user=None)
    public_url = reverse('schedules:public-schedule', kwargs={'public_id': public_id})
    res_pub = api_client.get(public_url)
    assert res_pub.status_code == status.HTTP_200_OK
    assert res_pub.data['student_name'] == student_user.full_name

    api_client.force_authenticate(user=student_user)
    del_url = reverse('schedules:share-link-detail', kwargs={'public_id': public_id})
    api_client.delete(del_url)

    api_client.force_authenticate(user=None)
    assert api_client.get(public_url).status_code == status.HTTP_404_NOT_FOUND
