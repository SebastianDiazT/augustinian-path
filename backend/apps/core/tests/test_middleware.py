import re

import pytest

UUID_RE = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)


@pytest.mark.django_db
def test_generates_a_new_request_id_when_client_sends_none(client):
    response = client.get('/api/v1/health/')

    assert 'X-Request-Id' in response
    assert UUID_RE.match(response['X-Request-Id'])


@pytest.mark.django_db
def test_reuses_incoming_request_id_header(client):
    incoming = '11111111-1111-1111-1111-111111111111'

    response = client.get('/api/v1/health/', HTTP_X_REQUEST_ID=incoming)

    assert response['X-Request-Id'] == incoming


@pytest.mark.django_db
def test_two_requests_without_incoming_header_get_different_ids(client):
    first = client.get('/api/v1/health/')
    second = client.get('/api/v1/health/')

    assert first['X-Request-Id'] != second['X-Request-Id']


def test_request_id_header_is_present_on_error_responses(client):
    response = client.get('/api/v1/this-route-does-not-exist/')

    assert response.status_code == 404
    assert 'X-Request-Id' in response
    assert UUID_RE.match(response['X-Request-Id'])
